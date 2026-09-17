from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from .builder import PROJECTS_DIR


def project_path(project_id: str) -> Path:
    candidate = (PROJECTS_DIR / project_id).resolve()
    if candidate.parent != PROJECTS_DIR.resolve() or not candidate.is_dir():
        raise HTTPException(status_code=404, detail="Project not found")
    return candidate


def preview_file(project_id: str, requested_path: str = "") -> FileResponse | HTMLResponse:
    project_dir = project_path(project_id)
    dist_dir = (project_dir / "dist").resolve()
    if dist_dir.parent != project_dir.resolve() or not dist_dir.is_dir():
        raise HTTPException(status_code=404, detail="Preview is not available")
    relative = requested_path or "index.html"
    target = (dist_dir / relative).resolve()
    if dist_dir not in target.parents and target != dist_dir:
        raise HTTPException(status_code=404, detail="Preview file not found")
    if target.is_dir():
        target = target / "index.html"
    if not target.is_file():
        target = dist_dir / "index.html"
    if target.name == "index.html":
        html = target.read_text(encoding="utf-8")
        asset_prefix = f"/preview/{project_id}/assets/"
        html = html.replace('src="/assets/', f'src="{asset_prefix}')
        html = html.replace('href="/assets/', f'href="{asset_prefix}')
        return HTMLResponse(html)
    return FileResponse(target)
