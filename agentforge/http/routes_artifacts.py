from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from agentforge.http.auth import get_store, require_operator

router = APIRouter()


@router.get("/operator/artifacts/{relative_path:path}")
def get_artifact(
    relative_path: str,
    operator: str = Depends(require_operator),
    store=Depends(get_store),
):
    try:
        path = store.safe_artifact_path(relative_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="artifact not found")
    return FileResponse(path)
