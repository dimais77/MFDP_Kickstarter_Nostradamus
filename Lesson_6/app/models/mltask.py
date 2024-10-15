from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSON
from typing import Optional, Any
from datetime import datetime


class MLTask(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    model_id: int = Field(foreign_key="mlmodel.model_id", default=1)
    input_data: Any = Field(sa_column=Column(JSON))
    status: str = Field(default="new")
    output_data: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
