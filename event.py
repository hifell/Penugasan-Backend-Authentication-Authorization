from sqlalchemy import Column, Integer, String
from connection import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    quota = Column(Integer, nullable=False)