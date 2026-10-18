import os
import re
import uuid
import shutil
import logging
from pathlib import Path
from typing import Tuple, Union
import aiofiles
from fastapi import HTTPException, UploadFile, status

from app.config import settings

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".pdf", ".webp"}


def validate_file_extension(filename: str) -> str:
    """Validate that the file extension is supported."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Supported formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    return ext


def get_file_page_count(file_path: Path) -> int:
    """Determine the number of pages for PDF or image."""
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        try:
            from pdf2image import pdfinfo_from_path
            kwargs = {}
            if settings.POPPLER_PATH:
                kwargs["poppler_path"] = settings.POPPLER_PATH
            info = pdfinfo_from_path(str(file_path), **kwargs)
            return int(info.get("Pages", 1))
        except Exception as e:
            logger.warning(f"Could not read PDF page count with pdf2image for {file_path}: {e}")
            # Fallback simple PDF page count heuristic
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                    matches = re.findall(rb"/Type\s*/Page\b", content)
                    if matches:
                        return len(matches)
            except Exception:
                pass
            return 1
    return 1


async def save_upload_file(
    upload_file: UploadFile, destination_dir: Path = settings.UPLOAD_DIR
) -> Tuple[Path, str, int, int]:
    """
    Saves an uploaded file with a UUID-based filename to the uploads directory.
    Returns: (saved_file_path, unique_filename, file_size_in_bytes, page_count)
    """
    destination_dir.mkdir(parents=True, exist_ok=True)
    orig_name = upload_file.filename or "unknown_file"
    ext = validate_file_extension(orig_name)
    
    clean_stem = re.sub(r"[^\w\-_\.]", "_", Path(orig_name).stem)[:40]
    unique_filename = f"{uuid.uuid4().hex}_{clean_stem}{ext}"
    target_path = destination_dir / unique_filename

    file_size = 0
    try:
        async with aiofiles.open(target_path, "wb") as out_file:
            while chunk := await upload_file.read(1024 * 64):  # 64KB chunks
                file_size += len(chunk)
                if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                    # Clean up file on limit exceeded
                    await out_file.close()
                    if target_path.exists():
                        target_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB",
                    )
                await out_file.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        if target_path.exists():
            target_path.unlink(missing_ok=True)
        logger.error(f"Failed to save uploaded file {orig_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save uploaded file: {str(e)}",
        )

    page_count = get_file_page_count(target_path)
    return target_path, unique_filename, file_size, page_count


def copy_local_file_to_uploads(
    source_path: Path, destination_dir: Path = settings.UPLOAD_DIR
) -> Tuple[Path, str, int, int]:
    """
    Copies a local file (e.g., from demo_docs) into the uploads directory with a unique UUID.
    Returns: (saved_file_path, unique_filename, file_size_in_bytes, page_count)
    """
    destination_dir.mkdir(parents=True, exist_ok=True)
    ext = validate_file_extension(source_path.name)
    
    clean_stem = re.sub(r"[^\w\-_\.]", "_", source_path.stem)[:40]
    unique_filename = f"{uuid.uuid4().hex}_{clean_stem}{ext}"
    target_path = destination_dir / unique_filename

    shutil.copyfile(source_path, target_path)
    file_size = target_path.stat().st_size
    page_count = get_file_page_count(target_path)
    return target_path, unique_filename, file_size, page_count


def infer_doc_type_from_filename(filename: str) -> str:
    """
    Infers document type ('khatian', 'porcha', 'deed') from filename prefix or keywords.
    Defaults to 'khatian' if not identifiable.
    """
    lower = filename.lower()
    if any(k in lower for k in ["khatian", "khotian", "cs_", "rs_", "sa_", "bs_"]):
        return "khatian"
    if any(k in lower for k in ["porcha", "parcha", "porca"]):
        return "porcha"
    if any(k in lower for k in ["deed", "dolil", "dalil", "saf_kobla", "hiba"]):
        return "deed"
    return "khatian"


def delete_file(file_path: Union[str, Path]) -> bool:
    """Deletes a file from the filesystem safely."""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    except Exception as e:
        logger.warning(f"Failed to delete file {file_path}: {e}")
        return False
