from enum import Enum
from pathlib import Path
from dependencies import doc_processor, vector_store
from fastapi import APIRouter, File, UploadFile, HTTPException, status, BackgroundTasks

fileRouter = APIRouter(prefix="/files", tags=["File handling"])
queryRouter = APIRouter(prefix="/query", tags=["Query"])

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


@queryRouter.post("/retrieve/")
def retrieve_top_chunks(text: str | None = None, top_k: int | None = None):
    if not text:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Query must not be empty",
        )

    data = vector_store.query_data(text, top_k)
    return data
