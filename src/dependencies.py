from rag_system.retriever import VectorStore
from rag_system.document_processor import DocumentProcessor
from rag_system.generator import LLMService

import cohere
from google import genai
from dotenv import dotenv_values

from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

config = dotenv_values("../.env")

embedder: embedding_functions = ONNXMiniLM_L6_V2()  # AKA bi-encoder

cross_encoder = cohere.ClientV2(
    api_key=config.get("COHERE_API_KEY"), client_name="rag-reranker"
)

ai_client = genai.Client(api_key=config.get("GEMINI_API_KEY"))

# Singleton instance
vector_store = VectorStore(embedder=embedder, reranker=cross_encoder)
doc_processor = DocumentProcessor(vector_store, embedder=embedder)
llm_service = LLMService(llm_provider=ai_client, model="gemini-3.5-flash")
