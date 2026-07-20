from google.genai import Client

TEMPLATE = """
You are a retrieval-augmented AI assistant.

You MUST answer ONLY from the retrieved context.

## Rules

1. Use only the retrieved context.
2. Do not use prior knowledge, assumptions, or common sense to fill in missing information.
3. If the context does not explicitly contain the answer, respond exactly with:
   "I cannot answer this question based on the provided information."
4. If multiple retrieved documents contain relevant information, combine them faithfully.
5. Do not contradict the retrieved context.
6. Do not fabricate names, dates, numbers, or explanations.
7. When information comes from a document, cite its document ID if available.

## Retrieved Context

{user_retrieved_context}

## User Question

{user_query}

## Response

- Answer in the same language as the user's question.
- Keep the response clear and concise.
- Include document citations where applicable.
"""


class LLMService:
    def __init__(self, llm_provider: Client, model: str = "gemini-3.5-flash"):
        self.llm_provider = llm_provider
        self.model = model

    def query_llm(self, query: str, docs: list[str]):  # -> str
        if not query.strip():
            return "Query must not be empty."

        if not docs:
            return "I cannot answer this question based on the provided information."

        context = "\n\n".join([f"{i+1}. {doc}" for i, doc in enumerate(docs)])

        prompt = TEMPLATE.format(user_retrieved_context=context, user_query=query)

        interaction = self.llm_provider.interactions.create(
            model=self.model,
            input=prompt,
        )

        return interaction
