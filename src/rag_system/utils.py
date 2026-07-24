import logging
import colorlog
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    STARTED = "started"
    FAILURE = "failure"
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    SKIPPED = "skipped"


class MetadataTemplate(BaseModel):
    total_chunks: int
    filename: str
    filetype: str
    token_size: int
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


class PipelineSchema(BaseModel):
    # id: int
    filename: str
    type: Optional[str] = None
    chunks: Optional[int] = 0
    size: Optional[int] = 0
    status: ProcessingStatus = ProcessingStatus.STARTED
    desc: Optional[str] = "Document under staging"


handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
