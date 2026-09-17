import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agents.architect import architect_agent
from agents.coder import coder_agent
from agents.planner import planner_agent
from agents.validator import validator_agent
from utils.file_writer import write_files
from .builder import bootstrap_project, build_project, next_project_dir, write_generated_files

Progress = Callable[[str, str, str | None], None]


def is_rate_limit_error(error: Exception) -> bool:
    return getattr(error, "status_code", None) == 429 or "rate limit" in str(error).lower() or "tokens per day" in str(error).lower()


def generate_project(prompt: str, progress: Progress | None = None) -> dict:
    def report(stage: str, status: str, detail: str | None = None) -> None:
        if progress:
            progress(stage, status, detail)

    state = {"user_prompt": prompt, "attempt": 1}
    report("planner", "running")
    state.update(planner_agent(state))
    report("planner", "completed")

    report("architect", "running")
    state.update(architect_agent(state))
    report("architect", "completed")

    validation = {"status": "fail", "issues": ["Validation did not run"]}
    for attempt in range(1, 4):
        state["attempt"] = attempt
        report("coder", "running", f"Attempt {attempt} of 3")
        try:
            state.update(coder_agent(state))
        except Exception as error:
            if is_rate_limit_error(error):
                report("coder", "failed", "Groq rate limit reached")
                raise RuntimeError("Groq rate limit reached. Wait for the quota to reset or update the Groq API plan.") from error
            validation = {
                "status": "fail",
                "issues": [f"Coder output could not be parsed: {type(error).__name__}"],
                "suggested_fixes": ["Return only a valid JSON object mapping source file paths to code"],
            }
            report("coder", "failed", validation["issues"][0])
            if attempt < 3:
                state["validation"] = validation
                continue
            raise RuntimeError("Coder failed to return valid source code after 3 attempts") from error
        report("coder", "completed", f"Attempt {attempt} of 3")
        report("validator", "running")
        state.update(validator_agent(state))
        validation = state.get("validation", {})
        if validation.get("status") == "pass":
            report("validator", "completed")
            break
        report("validator", "failed", "; ".join(validation.get("issues", [])))
        if attempt < 3:
            state["validation"] = validation
    else:
        raise RuntimeError("Generated code did not pass validation after 3 attempts")

    report("building", "running")
    plan = state.get("plan", {})
    project_id, project_dir = next_project_dir(plan.get("app_name", "generated-app"))
    bootstrap_project(project_dir)
    write_generated_files(project_dir, state["code"])
    build_project(project_dir)
    report("building", "completed")
    report("preview", "completed")

    metadata = {
        "projectId": project_id,
        "name": plan.get("app_name", project_id),
        "prompt": prompt,
        "status": "completed",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "validation": validation,
        "files": state["code"],
    }
    (project_dir / ".autosite.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata
