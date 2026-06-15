from __future__ import annotations

import mimetypes
import re
import shutil
import uuid
from pathlib import Path
from typing import Any, BinaryIO, Optional

from PIL import Image, UnidentifiedImageError


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_UPLOAD_DIR = BASE_DIR / "data" / "uploads"

PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg"}

MAX_PHOTO_SIZE_BYTES = 10 * 1024 * 1024
MAX_AUDIO_SIZE_BYTES = 25 * 1024 * 1024


def sanitize_filename(filename: str) -> str:
    """
    Return a filesystem-safe version of the original filename.
    """
    original = Path(filename).name
    stem = Path(original).stem
    suffix = Path(original).suffix.lower()

    safe_stem = re.sub(r"[^A-Za-z0-9_-]+", "_", stem).strip("_")
    safe_stem = safe_stem[:80] or "uploaded_file"

    return f"{safe_stem}{suffix}"


def detect_material_type(filename: str) -> str:
    """
    Detect whether an uploaded file is a Photo or Audio file.
    """
    suffix = Path(filename).suffix.lower()

    if suffix in PHOTO_EXTENSIONS:
        return "Photo"

    if suffix in AUDIO_EXTENSIONS:
        return "Audio"

    raise ValueError(
        "Unsupported file type. Supported photo types: "
        f"{sorted(PHOTO_EXTENSIONS)}; supported audio types: "
        f"{sorted(AUDIO_EXTENSIONS)}."
    )


def validate_upload(
    filename: str,
    file_size_bytes: int,
    mime_type: Optional[str] = None,
) -> str:
    """
    Validate extension, size and optional MIME type.

    Returns:
        "Photo" or "Audio"
    """
    if not filename.strip():
        raise ValueError("filename cannot be empty.")

    if file_size_bytes <= 0:
        raise ValueError("The uploaded file is empty.")

    material_type = detect_material_type(filename)
    suffix = Path(filename).suffix.lower()

    if material_type == "Photo":
        if file_size_bytes > MAX_PHOTO_SIZE_BYTES:
            raise ValueError("Photo size exceeds the 10 MB limit.")

        if mime_type and not mime_type.startswith("image/"):
            raise ValueError(
                f"Invalid photo MIME type: {mime_type}"
            )

    if material_type == "Audio":
        if file_size_bytes > MAX_AUDIO_SIZE_BYTES:
            raise ValueError("Audio size exceeds the 25 MB limit.")

        accepted_audio_mime_types = {
            "audio/mpeg",
            "audio/mp3",
            "audio/wav",
            "audio/x-wav",
            "audio/mp4",
            "audio/x-m4a",
            "audio/aac",
            "audio/ogg",
            "application/octet-stream",
        }

        if mime_type and mime_type not in accepted_audio_mime_types:
            guessed_type, _ = mimetypes.guess_type(filename)

            if not (guessed_type and guessed_type.startswith("audio/")):
                raise ValueError(
                    f"Invalid audio MIME type: {mime_type}"
                )

    if suffix not in PHOTO_EXTENSIONS | AUDIO_EXTENSIONS:
        raise ValueError("Unsupported file extension.")

    return material_type


def _read_file_bytes(file_source: bytes | BinaryIO) -> bytes:
    """
    Read bytes from raw bytes or a file-like object.
    """
    if isinstance(file_source, bytes):
        return file_source

    if hasattr(file_source, "seek"):
        file_source.seek(0)

    data = file_source.read()

    if hasattr(file_source, "seek"):
        file_source.seek(0)

    if not isinstance(data, bytes):
        raise TypeError("Uploaded file content must be bytes.")

    return data


def _verify_photo(photo_path: Path) -> None:
    """
    Use Pillow to verify that a saved photo is a valid image.
    """
    try:
        with Image.open(photo_path) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        photo_path.unlink(missing_ok=True)
        raise ValueError(
            "The uploaded photo could not be verified as a valid image."
        ) from exc


def save_uploaded_file(
    file_source: bytes | BinaryIO,
    original_filename: str,
    project_id: int,
    mime_type: Optional[str] = None,
    upload_dir: Path | str = DEFAULT_UPLOAD_DIR,
) -> dict[str, Any]:
    """
    Validate and save an uploaded photo or audio file.

    A unique filename is generated to avoid collisions.

    Returns a metadata dictionary that can be passed to
    database.add_file_material().
    """
    if project_id <= 0:
        raise ValueError("project_id must be a positive integer.")

    file_bytes = _read_file_bytes(file_source)
    file_size_bytes = len(file_bytes)

    material_type = validate_upload(
        filename=original_filename,
        file_size_bytes=file_size_bytes,
        mime_type=mime_type,
    )

    safe_original_name = sanitize_filename(original_filename)
    suffix = Path(safe_original_name).suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{suffix}"

    category_folder = (
        "photos" if material_type == "Photo" else "audio"
    )

    root = Path(upload_dir)
    target_dir = root / f"project_{project_id}" / category_folder
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / unique_name
    target_path.write_bytes(file_bytes)

    if material_type == "Photo":
        _verify_photo(target_path)

    try:
        relative_path = target_path.resolve().relative_to(
            BASE_DIR.resolve()
        )
        stored_path = relative_path.as_posix()
    except ValueError:
        stored_path = str(target_path.resolve())

    resolved_mime = (
        mime_type
        or mimetypes.guess_type(original_filename)[0]
        or "application/octet-stream"
    )

    return {
        "material_type": material_type,
        "original_filename": Path(original_filename).name,
        "stored_filename": unique_name,
        "stored_path": stored_path,
        "mime_type": resolved_mime,
        "file_size_bytes": file_size_bytes,
        "absolute_path": str(target_path.resolve()),
    }


def delete_uploaded_file(
    stored_path: str,
    base_dir: Path | str = BASE_DIR,
) -> bool:
    """
    Delete an uploaded file only when it is inside the project directory.
    """
    base = Path(base_dir).resolve()
    candidate = Path(stored_path)

    if not candidate.is_absolute():
        candidate = base / candidate

    candidate = candidate.resolve()

    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError(
            "Refusing to delete a file outside the project directory."
        ) from exc

    if not candidate.exists():
        return False

    candidate.unlink()
    return True


def clear_project_uploads(
    project_id: int,
    upload_dir: Path | str = DEFAULT_UPLOAD_DIR,
) -> bool:
    """
    Remove all locally stored uploads for a project.
    Intended for local testing or explicit user deletion.
    """
    if project_id <= 0:
        raise ValueError("project_id must be a positive integer.")

    project_folder = Path(upload_dir) / f"project_{project_id}"

    if not project_folder.exists():
        return False

    shutil.rmtree(project_folder)
    return True
