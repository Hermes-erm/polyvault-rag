from rag_system.retriever import VectorStore
from rag_system.document_processor import DocumentProcessor

import cohere
from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

# from sentence_transformers import CrossEncoder

embedder: embedding_functions = ONNXMiniLM_L6_V2()  # AKA bi-encoder

# cross_encoder = CrossEncoder(
#     "cross-encoder/ms-marco-MiniLM-L6-v2",
#     local_files_only=True,  # False
# )

cross_encoder = cohere.ClientV2(
    api_key="bAyW3CDW3YttVy3ZHrOADTEHFkrPko79rvCHCIuo",
    client_name="rag-reranker",
)

# Singleton instance
vector_store = VectorStore(embedder=embedder, reranker=cross_encoder)
doc_processor = DocumentProcessor(vector_store, embedder=embedder)
