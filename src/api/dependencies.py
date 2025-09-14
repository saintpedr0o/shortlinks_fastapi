import uuid
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.exceptions import ExpiredTokenError, InvalidTokenError, UserNotFoundException
from src.models.user import User
from src.repositories.click import ClickRepository
from src.repositories.link import LinkRepository
from src.repositories.user import UserRepository
from src.services.auth import auth_service
from src.services.click import ClickService
from src.services.link import LinkService
from src.services.user import UserService

bearer_scheme = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


async def get_user_service() -> UserService:
    return UserService(UserRepository())


async def get_link_service() -> LinkService:
    return LinkService(LinkRepository())


async def get_click_service() -> ClickService:
    return ClickService(ClickRepository())


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db=Depends(get_db),
    user_service: UserService = Depends(get_user_service),
) -> User:
    token = credentials.credentials

    try:
        payload = auth_service.decode_access_token(token)
    except ExpiredTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = uuid.UUID(user_id_str)
    try:
        user = await user_service.get_user_by_id(db, user_id)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_active_user(user: User = Depends(get_current_user)):
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Deactivated account"
        )
    return user


async def superuser_required(current_user: User = Depends(get_current_user)) -> None:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions, you must be superuser",
        )
