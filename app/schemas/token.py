from pydantic import BaseModel, model_serializer
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime
    user_key: str

    @model_serializer
    def ser_model(self) -> dict:
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_at": self.expires_at.isoformat(),
            "user_key": self.user_key,
        }


class TokenData(BaseModel):
    username: str | None = None
