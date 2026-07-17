import chromadb
from chromadb.errors import NotFoundError
from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2

from pydantic import BaseModel
from datetime import datetime


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

vectorStore = chromadb.PersistentClient(path="./chromadb")
generic_collection = getVectorCollection()


class MetadataTemplate(BaseModel):
    total_chunks: int
    filename: str
    filetype: str
    title: str
    description: str
    time: datetime


def token_len(text):
    # return model
    pass


def storeChunks(chunks: list[str], embedder: ONNXMiniLM_L6_V2):
    print(f"Storing chunks of size ({len(chunks)})..")

    print(embedder.tokenizer())
    print(len(chunks))
    for i in chunks:
        print(i)
        print(len(i))
        print("-----------------")
