from enum import Enum
from pathlib import Path
from dependencies import doc_processor
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks

fileRouter = APIRouter(
    prefix="/files",
    tags=["File handling"],
)
staging_dir = Path("../../pipeline/staging")


class ContentType(Enum):
    # XLSX = "application/vnd.ms-excel"
    # JSON = "application/json"  # Optional
    PDF = "application/pdf"
    PNG = "image/png"
    JPEG = "image/jpeg"
    CSV = "text/csv"


@fileRouter.post("/import")
async def import_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):  # File(...): expect multipart/form-data rather than JSON
    if file.content_type not in ContentType:
        raise HTTPException(415, "Unsupported file type")

    with open(staging_dir / f"{file.filename}", "wb") as fileDest:
        content = await file.read()
        fileDest.write(content)

    background_tasks.add_task(doc_processor.run_pipeline, file.filename)

    return {"status": "File under processing"}
