from google.genai import Client
from dependencies import ai_client

TEMPLATE = """
"""


class LLMService:
    def __init__(self, llm_provider: Client, model: str = "gemini-3.5-flash"):
        self.llm_provider = llm_provider
        self.model = model
