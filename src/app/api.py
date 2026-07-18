from enum import Enum
from app.dependencies import doc_processor, vector_store
from fastapi import APIRouter, File, UploadFile, HTTPException

fileRouter = APIRouter(
    prefix="/files",
    tags=["File handling"],
)


class ContentType(Enum):
    # XLSX = "application/vnd.ms-excel"
    # JSON = "application/json"  # Optional
    PDF = "application/pdf"
    PNG = "image/png"
    JPEG = "image/jpeg"
    CSV = "text/csv"


@fileRouter.post("/import")
async def import_file(
    file: UploadFile = File(...),
):  # File(...): expect multipart/form-data rather than JSON
    if file.content_type not in ContentType:
        raise HTTPException(415, "Unsupported file type")

    doc_processor.run_pipeline(file)

    return {"status": "File under processing"}
