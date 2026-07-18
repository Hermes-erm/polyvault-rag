import time
import numpy as np
from pathlib import Path
from fastapi import UploadFile
from app.dependencies import vector_store
from blingfire import text_to_sentences

# from docling.document_extractor import DocumentExtractor
from docling.document_converter import DocumentConverter, MarkdownFormatOption
from docling.datamodel.base_models import InputFormat, ConversionStatus
from docling.datamodel.pipeline_options import PipelineOptions

from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2


class DocumentProcessor:

    def __init__(
        self,
        embedding_function: embedding_functions = ONNXMiniLM_L6_V2(),
    ):
        self.converter = DocumentConverter(
            allowed_formats=[
                InputFormat.MD,
                InputFormat.PDF,
                InputFormat.CSV,
                InputFormat.DOCX,
                InputFormat.XLSX,  # xls
                InputFormat.IMAGE,
                InputFormat.JSON_DOCLING,  # look at later
            ],
            format_options={
                InputFormat: MarkdownFormatOption(
                    pipeline_options=PipelineOptions(
                        document_timeout=50,
                        # artifacts_path="path/to/model"
                    )
                )
            },
        )
        self.embedder = embedding_function
        self.staging_dir = Path("../../pipeline/staging")
        self.processed_dir = Path("../../pipeline/processed")

    async def run_pipeline(self, file: UploadFile):
        with open(self.staging_dir / f"{file.filename}", "wb") as fileDest:
            content = await file.read()
            fileDest.write(content)

        conv_status, doc_filename = self._load_file(file.filename)

        if conv_status != ConversionStatus.SUCCESS:
            raise RuntimeError(
                f"Docling failed to convert '{file.filename}'. Status: {conv_status}"
            )

        # TODO: Track Doc status by class
        sentence_blocks = self._segmentize_doc(doc_filename)
        chunks = self._chunk_by_similarity(sentence_blocks)  # np.array(sentence_blocks)
        vector_store.store_chunks(chunks, self.staging_dir / f"{file.filename}")

    def _load_file(self, fileName: str):
        print("Staging file..")

        filePath = self.staging_dir / f"{fileName}"

        start_time = time.time()
        conv_result = self.converter.convert(source=filePath)  # conv_result.status

        doc_filename = conv_result.input.file.stem

        with open(
            self.processed_dir / f"{doc_filename}.md", "w", encoding="utf-8"
        ) as fp:
            fp.write(conv_result.document.export_to_markdown(image_placeholder=""))

        end_time = time.time() - start_time
        execution_time = end_time - start_time
        print(f"Document processed in {execution_time:.2f} seconds")

        # if filePath.exists(): # NOTE: later use
        #     filePath.unlink()
        #     print("File modified successfully.")
        # else:
        #     print("The file does not exist.")

        return conv_result.status, doc_filename

    def _segmentize_doc(self, fileName: str):
        print(f"Segmentizing file {fileName}.md ..")

        content = ""
        with open(self.processed_dir / f"{fileName}.md", "r") as md:
            content = md.read()

        sentence_blocks = text_to_sentences(content).splitlines()

        return sentence_blocks

    def _chunk_by_similarity(
        self, sentences: list[str], window: int = 2, percentile: float = 70
    ):
        print("Chunking..")

        n = len(sentences)

        if window >= n:
            raise ValueError(
                f"Window size ({window}) must be smaller than chunk count ({n})"
            )

        embeddings = self.embedder(sentences)
        distances = []

        for i in range(n - window):  # (win - 1)
            left_embedding = np.mean(embeddings[i : i + window], axis=0)
            right_embedding = np.mean(  # TODO: MEMOIZE
                embeddings[i + 1 : i + window + 1], axis=0
            )

            cosine = self._cosine_sim(left_embedding, right_embedding)
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

        return chunks

    def _cosine_sim(self, a: np.array, b: np.array):
        dot_prod = np.dot(a, b)  # a.b
        norm_vec = np.linalg.norm(a) * np.linalg.norm(b)  # |a| * |b|

        if norm_vec == 0.0:
            return 0.0

        return dot_prod / norm_vec  # a.b / |a||b|
