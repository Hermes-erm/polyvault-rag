from fastapi import FastAPI, File, UploadFile, HTTPException
from pathlib import Path

# from docling.document_extractor import DocumentExtractor
from docling.document_converter import DocumentConverter, MarkdownFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PipelineOptions

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

# filePath: str = "./multimodal/drylab.pdf"

# start_time = time.time()
# conv_result = converter.convert(source=filePath)
# end_time = time.time() - start_time

# print(conv_result.version, conv_result.status)

# doc_filename = conv_result.input.file.stem

# with open(f"{doc_filename}.md", "w", encoding="utf-8") as fp:
#     fp.write(conv_result.document.export_to_markdown())


@app.post("/file")
async def import_file(
    file: UploadFile = File(...),
):  # File(...): expect multipart/form-data rather than JSON

    with open(Path("./pipeline/staging") / f"{file.filename}", "wb") as fileDest:
        content = await file.read()
        fileDest.write(content)

    return {"data": file}
