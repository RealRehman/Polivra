
import os
import zipfile
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status


BACKEND_ROOT = Path(__file__).resolve().parents[2]

_storage_setting = os.getenv("DOCUMENT_STORAGE_PATH")
STORAGE_ROOT = (
    Path(_storage_setting).expanduser()
    if _storage_setting
    else BACKEND_ROOT / "private_documents"
)

if not STORAGE_ROOT.is_absolute():
    STORAGE_ROOT = BACKEND_ROOT / STORAGE_ROOT

STORAGE_ROOT = STORAGE_ROOT.resolve()

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_DOCX_UNCOMPRESSED_SIZE = 50 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _validate_file(file_path: Path, content_type: str) -> None:
    with file_path.open("rb") as source:
        signature = source.read(8)

    if content_type == "application/pdf":
        if not signature.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="File content does not match PDF format",
            )
        return

    if content_type == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        try:
            with zipfile.ZipFile(file_path) as archive:
                entries = archive.infolist()

                total_uncompressed_size = sum(
                    entry.file_size for entry in entries
                )

                if total_uncompressed_size > MAX_DOCX_UNCOMPRESSED_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="DOCX expands beyond the allowed size",
                    )

                names = {entry.filename for entry in entries}

                if (
                    "[Content_Types].xml" not in names
                    or "word/document.xml" not in names
                ):
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail="File is not a valid DOCX document",
                    )

                if any(
                    Path(name).is_absolute()
                    or ".." in Path(name).parts
                    for name in names
                ):
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail="Invalid DOCX archive paths",
                    )

        except zipfile.BadZipFile as exc:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="File is not a valid DOCX archive",
            ) from exc


async def save_document(upload: UploadFile) -> tuple[str, int]:
    content_type = upload.content_type or ""

    if content_type not in ALLOWED_CONTENT_TYPES:
        await upload.close()
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF and DOCX files are supported",
        )

    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)

    file_key = uuid4().hex
    file_path = STORAGE_ROOT / file_key
    total_size = 0

    try:
        with file_path.open("xb") as destination:
            while chunk := await upload.read(CHUNK_SIZE):
                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File exceeds the 10 MB limit",
                    )

                destination.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        _validate_file(file_path, content_type)

        return file_key, total_size

    except Exception:
        file_path.unlink(missing_ok=True)
        raise

    finally:
        await upload.close()


def delete_document_file(file_key: str) -> None:
    """Delete a file addressed by a generated storage key."""
    if not file_key or Path(file_key).name != file_key:
        raise ValueError("Invalid document storage key")

    file_path = (STORAGE_ROOT / file_key).resolve()

    if file_path.parent != STORAGE_ROOT:
        raise ValueError("Invalid document storage path")

    file_path.unlink(missing_ok=True)


def get_document_path(file_key: str) -> Path:
    if not file_key or Path(file_key).name != file_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    file_path = (STORAGE_ROOT / file_key).resolve()

    if file_path.parent != STORAGE_ROOT or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return file_path
