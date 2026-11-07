import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import get_settings


def save_attachment(file: UploadFile) -> str:
    settings = get_settings()
    base = Path(settings.attachments_dir)
    base.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "upload").suffix
    name = f"{uuid.uuid4().hex}{suffix}"
    dest = base / name

    with dest.open("wb") as out:
        out.write(file.file.read())

    if settings.gcs_bucket:
        try:
            from google.cloud import storage

            client = storage.Client(project=settings.gcp_project_id or None)
            bucket = client.bucket(settings.gcs_bucket)
            blob = bucket.blob(f"attachments/{name}")
            blob.upload_from_filename(str(dest), content_type=file.content_type)
            return f"gs://{settings.gcs_bucket}/attachments/{name}"
        except Exception:
            pass

    return str(dest)
