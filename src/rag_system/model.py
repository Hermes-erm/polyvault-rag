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
    size = Column(String, default="0 B")
    status = Column(String)
    desc = Column(String, default="No description provided")

    def __repr__(self):
        return f"Pipeline(id={self.id}, name={self.name}, status={self.status}, chunks={self.chunks}, size={self.size}, desc={self.desc})"


class PipelineRepository:
    def __init__(self):
        pass

    def get_all_docs(self, db: Session):
        docs = db.query(Pipeline).all()
        return docs

    def add_doc(self, db: Session, doc: PipelineSchema):
        doc_create = Pipeline(
            name=doc.filename,
            chunks=doc.chunks,
            size=self._format_bytes(doc.size),
            status=doc.status,
            desc=doc.desc,
        )

        db.add(doc_create)
        db.commit()
        db.refresh(doc_create)

        logger.debug("Data has been saved")
        logger.debug(doc_create)

        return doc_create

    def update_doc(self, db: Session, doc: PipelineSchema, doc_id: int):
        doc_result = db.query(Pipeline).filter(Pipeline.id == doc_id).first()

        setattr(doc_result, "status", doc.status)
        setattr(doc_result, "desc", doc.desc)
        setattr(doc_result, "chunks", doc.chunks)
        db.commit()
        db.refresh(doc_result)

        logger.debug("Data has been updated")
        logger.debug(doc_result)

        return doc_result

    def _format_bytes(self, byte_size: int):
        units = ["B", "KB", "MB", "GB"]

        for unit in units:
            if byte_size < 1024:
                return f"{byte_size:.2f} {unit}"
            byte_size = byte_size / 1024
