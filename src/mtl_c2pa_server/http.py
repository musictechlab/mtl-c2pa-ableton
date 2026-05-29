"""HTTP transport for the c2pa reader.

Local FastAPI server bound to loopback only, consumed by the M4L device in this
same repository. Click an audio clip in Ableton -> Node for Max POSTs the file
path here -> manifest summary appears in the device UI.
"""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from . import c2pa as c2pa_mod
from .c2pa import C2paError

logger = logging.getLogger("mtl_c2pa_server.http")

app = FastAPI(
    title="mtl-c2pa-http",
    description=(
        "Local HTTP C2PA reader for the mtl-c2pa-ableton Max for Live device. "
        "Loopback only."
    ),
    version="0.1.0",
)


class PathRequest(BaseModel):
    path: str = Field(
        ...,
        description="Absolute path to the media file (mp3, jpg, png, mp4, etc.).",
        examples=["/Users/me/Music/lyria_track.mp3"],
    )


class ScanRequest(BaseModel):
    directory: str = Field(..., description="Absolute path to the directory to scan.")
    recursive: bool = Field(
        True, description="Descend into subdirectories. Default true."
    )


def _error_payload(exc: Exception) -> dict[str, str]:
    return {"error": str(exc), "error_type": type(exc).__name__}


@app.exception_handler(FileNotFoundError)
async def _not_found_handler(request: Request, exc: FileNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content=_error_payload(exc))


@app.exception_handler(C2paError)
async def _c2pa_error_handler(request: Request, exc: C2paError) -> JSONResponse:
    return JSONResponse(status_code=400, content=_error_payload(exc))


@app.exception_handler(ValueError)
async def _value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content=_error_payload(exc))


@app.post("/summary")
def post_summary(req: PathRequest) -> dict[str, Any]:
    """Human-friendly summary of a file's C2PA manifest."""
    return c2pa_mod.summarize(req.path)


@app.post("/read")
def post_read(req: PathRequest) -> dict[str, Any]:
    """Full C2PA manifest store from a media file."""
    return c2pa_mod.read_manifest_store(req.path)


@app.post("/assertions")
def post_assertions(req: PathRequest) -> dict[str, Any]:
    """All assertions from the active manifest."""
    return c2pa_mod.list_assertions(req.path)


@app.post("/ingredients")
def post_ingredients(req: PathRequest) -> dict[str, Any]:
    """Ingredients (source assets) from the active manifest."""
    return c2pa_mod.list_ingredients(req.path)


@app.post("/verify")
def post_verify(req: PathRequest) -> dict[str, Any]:
    """Verify signature and validation state."""
    return c2pa_mod.verify(req.path)


@app.post("/scan")
def post_scan(req: ScanRequest) -> dict[str, Any]:
    """Scan a directory for C2PA-signed media files."""
    return c2pa_mod.scan_directory(req.directory, recursive=req.recursive)


@app.get("/info")
def get_info() -> dict[str, Any]:
    """c2pa-python library version and supported formats."""
    return c2pa_mod.library_info()


@app.get("/health")
def get_health() -> dict[str, str]:
    """Liveness probe for launchd / monitoring."""
    return {"status": "ok"}


def run() -> None:
    """Entry point for `poetry run mtl-c2pa-http`."""
    import uvicorn

    logging.basicConfig(level=logging.INFO)
    logger.info("Starting mtl-c2pa-http on 127.0.0.1:8765 (loopback only)")
    uvicorn.run(
        "mtl_c2pa_server.http:app",
        host="127.0.0.1",
        port=8765,
        log_level="info",
        reload=False,
    )
