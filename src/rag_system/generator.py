from google.genai import Client

TEMPLATE = """
You are an expert AI assistant tasked with answering user questions based *exclusively* on the provided retrieved context. 

### Guidelines:
1. **Context Adherence**: Rely *only* on the clear facts directly mentioned in the context. Do not assume, extrapolate, or use any prior knowledge. Any facts not directly mentioned in the context are considered completely untruthful.
2. **Missing Information**: If the answer cannot be found in the provided context, state exactly: "I cannot answer this question based on the provided information." Do not attempt to guess or invent an answer.
3. **Accuracy and Tone**: Provide accurate, well-structured, and objective responses. Match the language of the user's query.
4. **Citation**: Whenever possible, cite the specific information source or document ID provided in the context.

### Context:
<context>
{user_retrieved_context}
</context>

### User Query:
<question>
{user_query}
</question>

### Response:

"""


class LLMService:
    def __init__(self, llm_provider: Client, model: str = "gemini-3.5-flash"):
        self.llm_provider = llm_provider
        self.model = model

    def query_llm(self, query: str, docs: list[str]) -> str:
        if not query.strip():
            return "Quest Must not be empty!"

        prompt = TEMPLATE
        prompt = prompt.format(user_retrieved_context=docs, user_query=query)

        interaction = self.llm_provider.interactions.create(
            model=self.model,
            input=prompt,
        )

        return interaction
