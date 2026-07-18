import logging
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


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
