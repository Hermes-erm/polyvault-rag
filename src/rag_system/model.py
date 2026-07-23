from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Pipeline(Base):  # Table
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    chunks = Column(Integer)
    size = Column(Integer)
    status = Column(String)
    desc = Column(String, default="No description provided")


class PipelineRepository:
    def __init__(self):
        pass

    def add_doc(self):
        pass

    def update_doc_status(self):
        pass
