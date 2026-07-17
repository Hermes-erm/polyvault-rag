import chromadb
from chromadb.config import Settings
from chromadb.errors import NotFoundError
from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2

from pathlib import Path
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from transformers import AutoTokenizer


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
    "description": "A generic collection for all doc-type",
}

vectorStore = chromadb.PersistentClient(
    path="./chromadb", settings=Settings(allow_reset=True)  # TODO: add to .env
)
generic_collection = getVectorCollection()

tokenizer = AutoTokenizer.from_pretrained(
    pretrained_model_name_or_path="sentence-transformers/all-MiniLM-L6-v2",
    local_files_only=True,
)


class MetadataTemplate(BaseModel):  # NOTE: for later use
    total_chunks: int
    filename: str
    filetype: str
    token_size: int
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


def token_len(text):
    tokenie_txt = tokenizer(text, truncation=False, max_length=256)
    token_size = tokenie_txt["input_ids"]
    return len(token_size)


def storeChunks(chunks: list[str], embedder: ONNXMiniLM_L6_V2, filePath: Path):
    print(f"Storing chunks of size ({len(chunks)})..")

    ids = []
    meta_data = []
    embeddings = embedder(chunks)

    for i, chunk in enumerate(chunks):
        meta = {
            "total_chunks": len(chunks),
            "filename": filePath.name,
            "filetype": filePath.suffix,
            "token_size": token_len(chunk),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        id = f"{filePath}-{i}-{meta['token_size']}"

        meta_data.append(meta)
        ids.append(id)

    generic_collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=meta_data,
    )

    print(*generic_collection.get()["metadatas"])


if __name__ == "__main__":
    # vectorStore.reset()
    # print("Vector Collections: ", vectorStore.list_collections())
    pass
