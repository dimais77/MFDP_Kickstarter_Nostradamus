from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class MLModel(SQLModel, table=True):
    model_id: Optional[int] = Field(default=None, primary_key=True)
    model_name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

