from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    balance: float = 100.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int

class SignIn(SQLModel):
    username: str
    password: str

# class SignUp(SQLModel):
#     username:str
#     email: str
#     password: str


class GetUserResponse(SQLModel):
    id: int = Field(0)
    username: str = Field('')
    email: str = Field('')
    balance: int = Field(0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
