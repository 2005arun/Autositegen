import json
import logging
import os
import threading
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from services.builder import PROJECTS_DIR
from services.generator import generate_project
from services.preview import preview_file, project_path

app = FastAPI(title="AutoSiteGen API", version="1.0.0")
logger = logging.getLogger("autositegen")
allowed_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=2)
jobs: dict[str, dict[str, Any]] = {}
jobs_lock = threading.Lock()

STAGES = ["planner", "architect", "coder", "validator", "building", "preview"]


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=10, max_length=4000)


def is_quota_error(error: Exception) -> bool:
    current: BaseException | None = error
    while current:
        message = str(current).lower()
        if (
            getattr(current, "status_code", None) == 429
            or "rate limit" in message
            or "rate_limit" in message
            or "tokens per day" in message
            or "error code: 429" in message
        ):
            return True
        current = current.__cause__ or current.__context__
    return False


def set_job(job_id: str, **updates: Any) -> None:
    with jobs_lock:
        jobs[job_id].update(updates)


def run_generation(job_id: str, prompt: str) -> None:
    set_job(job_id, status="planning", currentAgent="planner", progress=5)

    def progress(stage: str, status: str, detail: str | None = None) -> None:
        stage_index = STAGES.index(stage) if stage in STAGES else 0
        percent = min(95, 8 + int((stage_index / len(STAGES)) * 82))
        if status == "completed":
            percent = min(95, percent + 10)
        with jobs_lock:
            stages = jobs[job_id].setdefault("stages", {})
            stages[stage] = status
            jobs[job_id].update(
                status="failed" if status == "failed" else ("building" if stage == "building" else stage),
                currentAgent=stage,
                progress=percent,
                detail=detail,
            )

    try:
        result = generate_project(prompt, progress)
        set_job(job_id, status="completed", currentAgent=None, progress=100, projectId=result["projectId"], result=result)
    except Exception as exc:
        logger.exception("Generation job %s failed", job_id)
        with jobs_lock:
            job = jobs[job_id]
            failed_stage = job.get("currentAgent") or "generation"
            if failed_stage in job.get("stages", {}):
                job["stages"][failed_stage] = "failed"
            message = str(exc)
            if not is_quota_error(exc) and "quota" not in message.lower() and not isinstance(exc, RuntimeError):
                message = f"Generation failed during {failed_stage}. Please try again."
            job.update(
                status="failed",
                currentAgent=None,
                progress=100,
                error=message,
            )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/generate", status_code=202)
def create_generation(request: GenerateRequest) -> dict[str, Any]:
    prompt = request.prompt.strip()
    if len(prompt) < 10:
        raise HTTPException(status_code=422, detail="Describe the website in at least 10 characters.")
    job_id = f"job-{uuid.uuid4().hex[:10]}"
    with jobs_lock:
        jobs[job_id] = {
            "jobId": job_id,
            "status": "queued",
            "currentAgent": None,
            "progress": 0,
            "stages": {stage: "pending" for stage in STAGES},
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
    executor.submit(run_generation, job_id, prompt)
    return jobs[job_id]


@app.get("/api/generate/{job_id}")
def get_generation(job_id: str) -> dict[str, Any]:
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    return job


def load_metadata(project_id: str) -> dict[str, Any]:
    path = project_path(project_id) / ".autosite.json"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Project metadata not found")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/projects")
def list_projects() -> list[dict[str, Any]]:
    if not PROJECTS_DIR.exists():
        return []
    projects = []
    for project_dir in PROJECTS_DIR.iterdir():
        metadata_path = project_dir / ".autosite.json"
        if metadata_path.is_file():
            projects.append(load_metadata(project_dir.name))
    return sorted(projects, key=lambda item: item.get("createdAt", ""), reverse=True)


@app.get("/api/projects/{project_id}")
def get_project(project_id: str) -> dict[str, Any]:
    return load_metadata(project_id)


@app.get("/api/projects/{project_id}/files")
def get_project_files(project_id: str) -> dict[str, Any]:
    metadata = load_metadata(project_id)
    return {"projectId": project_id, "files": metadata.get("files", {})}


@app.get("/api/projects/{project_id}/download")
def download_project(project_id: str) -> FileResponse:
    project_dir = project_path(project_id)
    archive_path = project_dir.with_suffix(".zip")
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in project_dir.rglob("*"):
            if file_path.is_file() and file_path.name != ".autosite.json":
                archive.write(file_path, file_path.relative_to(project_dir))
    return FileResponse(archive_path, filename=f"{project_id}.zip", media_type="application/zip")


@app.get("/preview/{project_id}")
def preview_root(project_id: str) -> FileResponse:
    return preview_file(project_id)


@app.get("/preview/{project_id}/{requested_path:path}")
def preview_asset(project_id: str, requested_path: str) -> FileResponse:
    return preview_file(project_id, requested_path)
