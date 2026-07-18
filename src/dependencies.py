from rag_system.retriever import VectorStore
from rag_system.document_processor import DocumentProcessor

from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

embedder: embedding_functions = ONNXMiniLM_L6_V2()

# Singleton instance
vector_store = VectorStore(embedder=embedder)
doc_processor = DocumentProcessor(vector_store, embedder=embedder)
