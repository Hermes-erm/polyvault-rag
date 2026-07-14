from fastapi import FastAPI, File, UploadFile, HTTPException
from pathlib import Path
from enum import Enum


from extract import loadFile

app = FastAPI()


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
