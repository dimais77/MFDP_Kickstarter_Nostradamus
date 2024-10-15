from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class TransactionHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    transaction_type: str
    amount: float
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
