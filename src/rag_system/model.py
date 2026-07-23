from sqlalchemy import Column, Integer, String
from dependencies import Base


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    chunks = Column(Integer)
    size = Column(Integer)
    status = Column(String)
