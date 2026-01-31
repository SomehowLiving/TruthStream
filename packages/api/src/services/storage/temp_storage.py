"""
Temporary file storage for uploads - computes hash and saves for processing.
"""
import hashlib
import mimetypes
from pathlib import Path
from typing import Any

import aiofiles
from fastapi import UploadFile


UPLOAD_DIR = Path("./tmp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed image MIME types for Phase 1
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}


def _detect_mime(content: bytes, filename: str | None) -> str:
    """Detect MIME type from content or filename."""
    # Try mimetypes from filename
    if filename:
        mime, _ = mimetypes.guess_type(filename)
        if mime:
            return mime
    # Fallback: check magic bytes
    if content[:4] == b"\xff\xd8\xff":
        return "image/jpeg"
    if content[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if content[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp"
    return "application/octet-stream"


async def save_upload_file(file: UploadFile) -> dict[str, Any]:
    """
    Save uploaded file and return metadata including SHA-256 hash.

    Args:
        file: FastAPI UploadFile

    Returns:
        Dict with content_hash, file_path, filename, mime_type, size
    """
    content = await file.read()
    content_hash = hashlib.sha256(content).hexdigest()
    mime = _detect_mime(content, file.filename or "")

    file_path = UPLOAD_DIR / f"{content_hash}_{file.filename or 'upload'}"
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return {
        "content_hash": content_hash,
        "file_path": str(file_path),
        "filename": file.filename or "upload",
        "mime_type": mime,
        "size": len(content),
    }


def extract_text_from_file(file_path: str, mime_type: str) -> str:
    """Extract text context for search (basic - images return placeholder)."""
    if mime_type.startswith("text/"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""
    if mime_type.startswith("image/"):
        return "[Image - use filename or hash for search]"
    return "[Binary content]"
