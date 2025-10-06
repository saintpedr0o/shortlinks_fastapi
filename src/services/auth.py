from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from jose import JWTError
from src.exceptions import ExpiredTokenError, InvalidTokenError
from src.models.auth import RefreshToken
from src.repositories.auth import AuthRepository
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from src.utils.jwt import encode_jwt, decode_jwt
from src.config import get_settings

settings = get_settings()


class AuthService:
    def __init__(self, auth_repository: AuthRepository):
        self._auth_repository = auth_repository

    async def _revoke_token(self, db: AsyncSession, token: RefreshToken) -> None:
        token.revoked = True
        await self._auth_repository.update_obj(db, token)

    async def create_access_token(self, data: Dict[str, Any]) -> str:
        return encode_jwt(
            data=data,
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )

    async def decode_refresh_token(self, token: str) -> Dict[str, Any]:
        try:
            return decode_jwt(token, settings.refresh_secret_key, settings.algorithm)
        except JWTError as e:
            if "Signature has expired" in str(e):
                raise ExpiredTokenError("Refresh token expired")
            raise InvalidTokenError("Invalid refresh token")

    async def create_refresh_token(self, db: AsyncSession, data: Dict[str, Any]) -> str:
        user_id = data["sub"]
        old_token = await self._auth_repository.get_active_by_user(db, user_id)
        if old_token:
            await self._revoke_token(db, old_token)

        jti = str(uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        payload = {**data, "jti": jti}

        token = encode_jwt(
            data=payload,
            secret_key=settings.refresh_secret_key,
            algorithm=settings.algorithm,
            expires_delta=timedelta(days=settings.refresh_token_expire_days),
        )

        db_token = RefreshToken(
            jti=jti,
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
        await self._auth_repository.create_obj(db, db_token)
        return token

    async def refresh_token(
        self, db: AsyncSession, refresh_token: str
    ) -> Dict[str, Any]:
        payload = await self.decode_refresh_token(refresh_token)
        jti = payload["jti"]
        user_id = payload["sub"]

        db_token = await self._auth_repository.get_by_jti(db, jti, user_id)
        if not db_token or db_token.revoked:
            raise InvalidTokenError("Invalid or revoked refresh token")

        await self._revoke_token(db, db_token)

        token_data = {"sub": user_id, "username": payload["username"]}
        new_refresh_token = await self.create_refresh_token(db, token_data)
        new_access_token = await self.create_access_token(token_data)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
