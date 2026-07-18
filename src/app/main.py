from fastapi import FastAPI
from .api import fileRouter

app = FastAPI(
    title="Poly-vault",
    description="",
    docs_url="/",  # docs_url="/docs"
)

app.include_router(
    fileRouter,
    prefix="/rag",
)
