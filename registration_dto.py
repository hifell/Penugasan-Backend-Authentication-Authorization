from pydantic import BaseModel
from typing import Optional

class RegistrationCreate(BaseModel):
    user_id: int
    event_id: int

class RegistrationUpdate(BaseModel):
    user_id: Optional[int] = None
    event_id: Optional[int] = None

class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int

    class Config:
        from_attributes = True