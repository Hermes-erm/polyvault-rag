import time
import numpy as np
from pathlib import Path
from .utils import logger, ProcessingStatus, PipelineSchema
from sqlalchemy.orm import Session
from .retriever import VectorStore
from .model import PipelineRepository
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
        vector_store: VectorStore,
        repository: PipelineRepository,
        embedder: embedding_functions = ONNXMiniLM_L6_V2(),
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
        self.embedder = embedder
        self.vector_store = vector_store
        self.repository = repository
        self.staging_dir = Path("../../pipeline/staging")
        self.processed_dir = Path("../../pipeline/processed")

    def run_pipeline(self, filename: str, db: Session):
        filePath = self.staging_dir / f"{filename}"

        doc_create = self.repository.add_doc(
            db, PipelineSchema(filename=filename, size=filePath.stat().st_size)
        )

        conv_status, doc_filename = self._load_file(filename)

        if conv_status != ConversionStatus.SUCCESS:
            self.repository.add_doc(
                db,
                PipelineSchema(
                    filename=filename,
                    desc="Converstion failed",
                    status=ProcessingStatus.FAILED,
                ),
            )
            raise RuntimeError(
                f"Docling failed to convert '{filename}'. Status: {conv_status}"
            )

        # TODO: Track Doc status by class
        sentence_blocks = self._segmentize_doc(doc_filename)

        self.repository.update_doc(
            db,
            PipelineSchema(
                filename=doc_create.name,
                status=ProcessingStatus.EMBEDDING,
                desc="File under embedding",
            ),
            doc_id=doc_create.id,
        )

        chunks = self._chunk_by_similarity(sentence_blocks)

        self.vector_store.store_chunks(chunks, filePath)

        self.repository.update_doc(
            db,
            PipelineSchema(
                filename=doc_create.name,
                chunks=len(chunks),
                status=ProcessingStatus.INDEXED,
                desc="File has been saved",
            ),
            doc_id=doc_create.id,
        )

        if filePath.exists():
            filePath.unlink()
            logger.info(f"File {filename} modified successfully.")
        else:
            logger.warning(f"The file {filename} does not exist.")

    def _load_file(self, fileName: str):
        logger.info("Staging file..")

        filePath = self.staging_dir / f"{fileName}"

        start_time = time.time()
        conv_result = self.converter.convert(source=filePath)  # conv_result.status

        doc_filename = conv_result.input.file.stem

        with open(
            self.processed_dir / f"{doc_filename}.md", "w", encoding="utf-8"
        ) as fp:
            fp.write(conv_result.document.export_to_markdown(image_placeholder=""))

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Document processed in {execution_time:.2f} seconds")

        return conv_result.status, doc_filename

    def _segmentize_doc(self, fileName: str):
        logger.info(f"Segmentizing file {fileName}.md ..")

        with open(self.processed_dir / f"{fileName}.md", "r") as md:
            content = md.read()

        sentence_blocks = text_to_sentences(content).splitlines()

        return sentence_blocks

    def _chunk_by_similarity(
        self, sentences: list[str], window: int = 2, percentile: float = 70
    ):
        logger.info("Chunking..")

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
