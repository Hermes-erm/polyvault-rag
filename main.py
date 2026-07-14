from fastapi import FastAPI, File, UploadFile, HTTPException
from pathlib import Path
from enum import Enum

# from docling.document_extractor import DocumentExtractor
from docling.document_converter import DocumentConverter, MarkdownFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PipelineOptions

from extract import loadFile

app = FastAPI()

converter = DocumentConverter(
    allowed_formats=[
        InputFormat.PDF,
        InputFormat.DOCX,
        InputFormat.JSON_DOCLING,  # look at later
        InputFormat.IMAGE,
        InputFormat.MD,
        InputFormat.CSV,
        InputFormat.XLSX,
    ],
    format_options={
        InputFormat: MarkdownFormatOption(
            pipeline_options=PipelineOptions(  # artifacts_path=""
                document_timeout=50,
            )
        ),
    },
)


fileStagePath = Path("./pipeline/staging")


class ContentType(Enum):
    # JSON = "application/json"  # Optional
    PDF = "application/pdf"
    PNG = "image/png"
    JPEG = "image/jpeg"
    CSV = "text/csv"
    XLSX = "application/vnd.ms-excel"


@app.post("/file")
async def import_file(
    file: UploadFile = File(...),
):  # File(...): expect multipart/form-data rather than JSON

    if file.content_type not in ContentType:
        raise HTTPException(415, "Unsupported file type")

    with open(fileStagePath / f"{file.filename}", "wb") as fileDest:
        content = await file.read()
        fileDest.write(content)

    resp = loadFile(file.filename)

    return resp
