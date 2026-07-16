import chromadb
from chromadb.errors import NotFoundError


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
