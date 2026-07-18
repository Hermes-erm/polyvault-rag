import chromadb
from chromadb.config import Settings
from chromadb import Collection
from chromadb.errors import NotFoundError
from chromadb.utils import embedding_functions

from pathlib import Path
from datetime import datetime, timezone
from transformers import AutoTokenizer

VECTOR_STORE = chromadb.PersistentClient(
    path="../../chromadb",  # XXX: Path("../../chromadb").resolve()
    settings=Settings(allow_reset=True),  # TODO: add to .env
)


class VectorStore:
    def __init__(
        self,
        embedder: embedding_functions,
        collection_name: str = "multimodal",
    ):
        self.embedder = embedder
        self.tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path="sentence-transformers/all-MiniLM-L6-v2",
            local_files_only=True,
        )
        self.collection_name = collection_name
        self.collection_metadata = {
            "name": collection_name,
            "docType": "Multimodal",
            "description": "A generic collection for all doc-type",
        }

        self.collection = self._get_collection()

    def _get_collection(self) -> Collection:
        generic_collection = None

        try:
            generic_collection = VECTOR_STORE.get_collection(name=self.collection_name)
        except NotFoundError:
            generic_collection = VECTOR_STORE.create_collection(
                name=self.collection_name,
                metadata=self.collection_metadata,
                # embedding_function=self.embedder, # ONNXMiniLM_L6_V2()
            )

        return generic_collection

    def _token_len(self, text: str):
        tokenie_txt = self.tokenizer(text, truncation=False, max_length=256)
        token_size = tokenie_txt["input_ids"]
        return len(token_size)

    def store_chunks(self, chunks: list[str], filePath: Path):
        print(f"Storing chunks of size ({len(chunks)})..")

        ids = []
        meta_data = []
        embeddings = self.embedder(chunks)

        for i, chunk in enumerate(chunks):
            meta = {
                "total_chunks": len(chunks),
                "filename": filePath.name,
                "filetype": filePath.suffix,
                "token_size": self.token_len(chunk),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            id = f"{filePath}-{i}-{meta['token_size']}"

            meta_data.append(meta)
            ids.append(id)

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=meta_data,
        )

        print(*self.collection.get()["metadatas"])
