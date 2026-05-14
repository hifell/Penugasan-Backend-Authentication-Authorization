from sqlmodel import SQLModel, Field
from typing import Optional

class Log(SQLModel, table=True):
    __tablename__ = "logs"

    id: Optional[int] = Field(default=None, primary_key=True)

    account_id: int = Field(foreign_key="accounts.id")
    action: str
    entity: str
    entity_id: int