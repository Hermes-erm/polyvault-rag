import time
import numpy as np
from pathlib import Path
from blingfire import text_to_sentences

# from docling.document_extractor import DocumentExtractor
from docling.document_converter import DocumentConverter, MarkdownFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PipelineOptions

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


embedder = ONNXMiniLM_L6_V2()  # all-MiniLM-L6-v2

fileStagePath = Path("./pipeline/staging")
sourceFilePath = Path("./pipeline/processed")


def loadFile(fileName: str):
    print("Staging file..")

    filePath = fileStagePath / f"{fileName}"

    # start_time = time.time()
    conv_result = converter.convert(source=filePath)
    # end_time = time.time() - start_time

    print(conv_result.status)
    doc_filename = conv_result.input.file.stem

    with open(sourceFilePath / f"{doc_filename}.md", "w", encoding="utf-8") as fp:
        fp.write(conv_result.document.export_to_markdown(image_placeholder=""))

    if filePath.exists():
        filePath.unlink()
        print("File modified successfully.")
    else:
        print("The file does not exist.")

    segmentizeDoc(doc_filename)

    return conv_result.status


def segmentizeDoc(fileName: str):
    print(f"Segmentizing file {fileName}.md ..")

    content = ""
    with open(sourceFilePath / f"{fileName}.md", "r") as md:
        content = md.read()

    sentence_blocks = text_to_sentences(content).splitlines()

    chunkBySimilarity(np.array(sentence_blocks))


def cosine_sim(a: np.array, b: np.array):
    dot_prod = np.dot(a, b)  # a.b
    norm_vec = np.linalg.norm(a) * np.linalg.norm(b)  # |a| * |b|

    if norm_vec == 0.0:
        return 0.0

    return dot_prod / norm_vec  # a.b / |a||b|


def chunkBySimilarity(sentences: list[str], window: int = 2, percentile: float = 70):
    print("Chunking..")

    n = len(sentences)

    if window >= n:
        raise ValueError(
            f"Window size ({window}) must be smaller than chunk count ({n})"
        )

    embeddings = embedder(sentences)
    distances = []

    for i in range(n - window):  # (win - 1)
        left_embedding = np.mean(embeddings[i : i + window], axis=0)
        right_embedding = np.mean(  # TODO: MEMOIZE
            embeddings[i + 1 : i + window + 1], axis=0
        )

        cosine = cosine_sim(left_embedding, right_embedding)
        distances.append(1 - cosine)

    threshold = np.percentile(distances, percentile)
    offset = window - 1
    breakpoints = [
        i + offset for i, d in enumerate(distances) if d >= threshold
    ]  # Break at the peak

    chunks, start = [], 0
    for ind in breakpoints:
        content = " ".join(sentences[start : ind + 1])
        start = ind + 1
        chunks.append(content)

    rest_chunks = " ".join(sentences[start:])
    chunks.append(rest_chunks)

    # print(np.array(distances).reshape(-1, 1))
    # for chunk in chunks:
    #     print(chunk)
    #     print(len(chunk))
    #     print("----------------------------------------")

    return chunks


segmentizeDoc("prideprejudice")
