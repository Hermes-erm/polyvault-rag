from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from .utils import logger, PipelineSchema

Base = declarative_base()


class Pipeline(Base):  # Table
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    chunks = Column(Integer, default=0)
    size = Column(Integer, default=0)
    status = Column(String)
    desc = Column(String, default="No description provided")


class PipelineRepository:
    def __init__(self):
        pass

    def add_doc(self, db: Session, doc: PipelineSchema):
        logger.debug(doc.model_dump_json(indent=2))
        doc_create = Pipeline(
            name=doc.filename,
            chunks=doc.chunks,
            size=doc.size,
            status=doc.status,
            desc=doc.desc,
        )

        db.add(doc_create)
        db.commit()
        db.refresh(doc_create)

        logger.info("Data has been saved")
        logger.debug(doc_create)

        return doc_create

    def update_doc_status(self):
        pass
