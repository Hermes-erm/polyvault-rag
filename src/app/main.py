from fastapi import FastAPI
from .api import fileRouter, queryRouter

app = FastAPI(
    title="Poly-vault",
    description="",
    docs_url="/docs",  # docs_url="/"
)

app.include_router(fileRouter, prefix="/rag")
app.include_router(queryRouter)
