import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT_DIR / "templates" / "react-vite-tailwind"
PROJECTS_DIR = ROOT_DIR / "generated-sites"


def safe_project_name(name: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")
    return value or "generated-app"


def next_project_dir(app_name: str) -> tuple[str, Path]:
    PROJECTS_DIR.mkdir(exist_ok=True)
    existing = [path for path in PROJECTS_DIR.iterdir() if path.is_dir()]
    project_numbers = []
    for path in existing:
        match = re.match(r"app-(\d+)-", path.name)
        if match:
            project_numbers.append(int(match.group(1)))
    project_id = max(project_numbers, default=0) + 1
    project_id_name = f"app-{project_id:03d}-{safe_project_name(app_name)}"
    return project_id_name, PROJECTS_DIR / project_id_name


def bootstrap_project(project_dir: Path) -> None:
    if project_dir.exists():
        shutil.rmtree(project_dir)
    shutil.copytree(TEMPLATE_DIR, project_dir)


def build_project(project_dir: Path) -> None:
    npm_command = "npm.cmd" if os.name == "nt" else "npm"
    commands = (
        [npm_command, "install", "--no-audit", "--no-fund"],
        [npm_command, "run", "build"],
    )
    for command in commands:
        try:
            subprocess.run(
                command,
                cwd=project_dir,
                check=True,
                shell=os.name == "nt",
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            output = (error.stderr or error.stdout or "").strip()
            detail = output[-2000:] if output else "No build output was returned."
            raise RuntimeError(f"Build step failed: {command[1]}\n{detail}") from error
        except FileNotFoundError as error:
            raise RuntimeError(
                "Node.js/npm is not installed on the backend host. Deploy the backend with the included Dockerfile."
            ) from error


def write_generated_files(project_dir: Path, files: dict[str, str]) -> None:
    allowed_roots = ("src/",)
    allowed_extensions = {".jsx", ".tsx", ".js", ".ts", ".css"}
    project_root = project_dir.resolve()
    for filename, content in files.items():
        normalized = filename.replace("\\", "/").lstrip("/")
        if not normalized.startswith(allowed_roots) or Path(normalized).suffix not in allowed_extensions:
            continue
        target = (project_dir / normalized).resolve()
        if project_root not in target.parents:
            raise ValueError("Generated file path escapes project directory")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(content).strip() + "\n", encoding="utf-8")
