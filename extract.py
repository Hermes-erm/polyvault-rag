import time
from pathlib import Path
import pysbd

# from docling.document_extractor import DocumentExtractor
from docling.document_converter import DocumentConverter, MarkdownFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PipelineOptions

converter = DocumentConverter(
    allowed_formats=[
        InputFormat.PDF,
        InputFormat.DOCX,
        InputFormat.JSON_DOCLING,  # look at later
        InputFormat.IMAGE,
        InputFormat.MD,
        InputFormat.CSV,
        InputFormat.XLSX,  # xls
    ],
    format_options={
        InputFormat: MarkdownFormatOption(
            pipeline_options=PipelineOptions(  # artifacts_path=""
                document_timeout=50,
            )
        ),
    },
)

segmenter = pysbd.Segmenter(language="en", clean=True)

fileStagePath = Path("./pipeline/staging")
sourceFilePath = Path("./pipeline/processed")


def loadFile(fileName: str):
    filePath = fileStagePath / f"{fileName}"

    # with open(filePath, "rb") as file:
    #     content = file.read()
    #     print(content)

    # start_time = time.time()
    conv_result = converter.convert(source=filePath)
    # end_time = time.time() - start_time

    print(conv_result.status)
    doc_filename = conv_result.input.file.stem

    with open(sourceFilePath / f"{doc_filename}.md", "w", encoding="utf-8") as fp:
        fp.write(conv_result.document.export_to_markdown(image_placeholder=""))

    if filePath.exists():
        filePath.unlink()
        print("File deleted successfully.")
    else:
        print("The file does not exist.")

    chunkDoc(doc_filename)

    return conv_result.status


def chunkDoc(fileName: str):
    content = ""
    with open(sourceFilePath / f"{fileName}.md", "r") as md:
        content = md.read()

    sentence_blocks = segmenter.segment(content)

    for sentence in sentence_blocks:
        print(sentence)


def embedChunks(chunks: list[str]):
    pass
