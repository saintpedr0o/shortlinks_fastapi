from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db, get_user_service, get_auth_service
from src.exceptions import (
    ExpiredTokenError,
    InvalidPasswordException,
    InvalidTokenError,
    UserNotFoundException,
)
from src.schemas.auth import TokenInfo, RefreshRequest
from src.schemas.user import UserLogin
from src.services.user import UserService
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenInfo, status_code=status.HTTP_200_OK)
async def login_for_access_token(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = await user_service.authenticate_user(
            db, credentials.login, credentials.password
        )
    except (UserNotFoundException, InvalidPasswordException):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login or password"
        )

    token_data = {"sub": str(user.id), "username": user.username}

    return {
        "access_token": await auth_service.create_access_token(token_data),
        "refresh_token": await auth_service.create_refresh_token(db, token_data),
        "token_type": "bearer",
    }


@router.post("/token/refresh", response_model=TokenInfo, status_code=status.HTTP_200_OK)
async def refresh_access_token(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        return await auth_service.refresh_token(db, data.refresh_token)
    except ExpiredTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
