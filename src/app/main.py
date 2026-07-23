from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import fileRouter, queryRouter

app = FastAPI(
    title="Poly-vault",
    description="",
    docs_url="/docs",  # docs_url="/"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fileRouter, prefix="/rag")
app.include_router(queryRouter)

app.frontend("/", directory="static", fallback=None)  # fallback="404.html"
