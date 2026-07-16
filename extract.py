import time
from pathlib import Path
import pysbd
import numpy as np

# from docling.document_extractor import DocumentExtractor
from docling.document_converter import DocumentConverter, MarkdownFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PipelineOptions

import chromadb
from chromadb.errors import NotFoundError
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

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

embedder = ONNXMiniLM_L6_V2()  # all-MiniLM-L6-v2
# embeddings = embedder([student_info, club_info, university_info])


def getVectorCollection():
    generic_collection = None

    try:
        generic_collection = vectorStore.get_collection(name=collection_name)
    except NotFoundError:
        generic_collection = vectorStore.create_collection(
            name=collection_name,
            metadata=collection_metadata,
            # embedding_function=ONNXMiniLM_L6_V2(),
        )

    return generic_collection


collection_name = "multimodal"
collection_metadata = {
    "name": collection_name,
    "docType": "Multimodal",
    "description": "A generic collection for multimodal",
}

vectorStore = chromadb.PersistentClient(path="./chromadb")
generic_collection = getVectorCollection()

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

    segmentizeDoc(doc_filename)

    return conv_result.status


def segmentizeDoc(fileName: str):
    content = ""
    with open(sourceFilePath / f"{fileName}.md", "r") as md:
        content = md.read()

    sentence_blocks = segmenter.segment(content)

    # for sentence in sentence_blocks:
    #     print(sentence)

    chunkBySimilarity(sentence_blocks)


def chunkBySimilarity(sentences: list[str]):
    pass


def cosine_sim(a: np.array, b: np.array):
    dot_prod = np.dot(a, b)  # a.b
    norm_vec = np.linalg.norm(a) * np.linalg.norm(b)  # |a| * |b|

    if norm_vec == 0.0:
        return 0.0

    return dot_prod / norm_vec  # a.b / |a||b|
