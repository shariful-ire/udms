"""File handling utilities for profile image uploads."""
from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import InvalidFileTypeException, UploadTooLargeException


ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
}

MIME_TO_EXTENSION = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}

MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


async def save_avatar(file: UploadFile, user_id: str) -> str:
    """
    Validate and save an uploaded avatar image.
    Returns the public URL path (e.g. /uploads/avatars/user_id_abc123.jpg).
    Raises InvalidFileTypeException or UploadTooLargeException on failure.
    """
    # 1. Validate MIME type
    content_type = file.content_type or ""
    if content_type not in ALLOWED_MIME_TYPES:
        raise InvalidFileTypeException(list(ALLOWED_MIME_TYPES))

    # 2. Read content
    contents = await file.read()

    # 3. Validate size
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise UploadTooLargeException(MAX_FILE_SIZE_MB)

    # 4. Determine extension
    ext = MIME_TO_EXTENSION.get(content_type, "jpg")

    # 5. Build a unique filename (user_id + random suffix)
    suffix = uuid.uuid4().hex[:8]
    filename = f"{user_id}_{suffix}.{ext}"

    # 6. Ensure directory exists
    avatar_dir = Path(settings.UPLOAD_DIR) / "avatars"
    avatar_dir.mkdir(parents=True, exist_ok=True)

    # 7. Remove old avatar if desired (not required — just keep new one)
    dest_path = avatar_dir / filename
    with open(dest_path, "wb") as f:
        f.write(contents)

    return f"/uploads/avatars/{filename}"


def delete_file(url_path: str) -> None:
    """Delete a file by its URL path. Silently ignores missing files."""
    if not url_path or not url_path.startswith("/uploads/"):
        return
    relative = url_path.lstrip("/")
    full_path = Path(settings.UPLOAD_DIR).parent / relative
    try:
        full_path.unlink(missing_ok=True)
    except Exception:
        pass


def compute_file_hash(contents: bytes) -> str:
    """Compute SHA-256 hash of file contents (for deduplication)."""
    return hashlib.sha256(contents).hexdigest()
