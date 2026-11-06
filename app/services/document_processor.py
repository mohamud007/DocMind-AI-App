
from pathlib import Path
from uuid import uuid4

import pymupdf

UPLOAD_DIR = Path("data/uploads")
ALLOWED_EXTENSIONS = {".pdf", ".txt"}


def save_uploaded_document(filename: str, content: bytes) -> dict:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    original_name = Path(filename).name
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF and TXT files are supported.")

    saved_name = f"{uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / saved_name
    file_path.write_bytes(content)

    return {
        "original_filename": original_name,
        "saved_filename": saved_name,
        "size_bytes": len(content),
        "file_path": str(file_path)
    }


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".txt":
        return path.read_text(encoding="utf-8")

    if extension == ".pdf":
        with pymupdf.open(path) as document:
            pages = [
                page.get_text()
                for page in document
            ]

        return "\n".join(pages)

    raise ValueError("Unsupported document format.")
