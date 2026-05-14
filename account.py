from sqlmodel import SQLModel, Field
from typing import Optional

from pydantic import BaseModel

class Account(SQLModel, table=True):
    __tablename__ = "accounts"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="users.id")
    role_id: int = Field(foreign_key="roles.id")

    email: str
    username: str
    password: str

# untuk POST
class AccountCreate(BaseModel):
    name: str
    email: str

# untuk PUT
class AccountUpdate(BaseModel):
    name: str
    email: str

# untuk response Swagger
class AccountResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True