from sqlalchemy import Column, Integer, String
from src.database.connection import Base
from pydantic import BaseModel


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class RoleCreate(BaseModel):
    name: str

class RoleUpdate(BaseModel):
    name: str

class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True