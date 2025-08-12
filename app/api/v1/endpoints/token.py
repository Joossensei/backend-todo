from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas import Token
from typing import Annotated
from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.database import get_db
from sqlalchemy.orm import Session
from app.services import AuthService
from app.core.rate_limit import limiter
from slowapi.util import get_remote_address

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


@router.post("/token")
@limiter.limit("5/minute;100/hour", key_func=get_remote_address)
async def login_for_access_token(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    try:
        user = AuthService.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        access_token = AuthService.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return Token(
                access_token=access_token,
                token_type="bearer",
                expires_at=datetime.now(timezone.utc) + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS),
                user_key=user.key
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error while logging in (original error message: {e})")
