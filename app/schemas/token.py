from pydantic import BaseModel
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime
    user_key: str


class TokenData(BaseModel):
    username: str | None = None
