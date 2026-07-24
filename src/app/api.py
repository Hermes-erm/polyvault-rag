from enum import Enum
from pathlib import Path
from dependencies import doc_processor, vector_store, llm_service, pipeline, get_db
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    status,
    BackgroundTasks,
    Depends,
)

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
    TEXT = "text/plain"


@fileRouter.post("/import")
async def import_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):  # File(...): expect multipart/form-data rather than JSON
    if file.content_type not in ContentType:
        raise HTTPException(415, "Unsupported file type")

    with open(staging_dir / f"{file.filename}", "wb") as fileDest:
        content = await file.read()
        fileDest.write(content)

    background_tasks.add_task(doc_processor.run_pipeline, file.filename, db)

    return {"status": "File under processing"}


@fileRouter.get("/")
def get_all_files(db: Session = Depends(get_db)):
    docs = pipeline.get_all_docs(db)
    return docs


@queryRouter.get("/search")
def search(
    query: str,
    # db: Session = Depends(get_db), # NOTE: store conversation
):
    response = retrieve_top_chunks(query)
    result = llm_service.query_llm(query, response["documents"])
    return {"data": result}


@queryRouter.post("/retrieve/")
def retrieve_top_chunks(text: str | None = None, top_k: int = 3):
    if not text:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Query must not be empty",
        )

    data = vector_store.query_data(text, top_k)
    return data


@queryRouter.delete("/reset-vector/")
def reset_vector_store(collection: str | None = None):
    collection = collection if collection else vector_store.collection_name
    vector_store.reset_vector(collection)

    return {"message": f"Collection {collection} has been deleted"}
