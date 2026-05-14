from pydantic import BaseModel
from typing import Optional

class EventCreate(BaseModel):
    name: str
    description: str
    quota: int

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quota: Optional[int] = None

class EventResponse(BaseModel):
    id: int
    name: str
    description: str
    quota: int

    class Config:
        from_attributes = True