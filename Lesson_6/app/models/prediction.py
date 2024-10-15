from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class PredictionHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    model_id: int = Field(foreign_key="mlmodel.model_id")
    input_data: str
    output_data: str
    credits_used: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
