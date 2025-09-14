from datetime import timedelta
from typing import Dict, Any
from jose import JWTError
from src.exceptions import ExpiredTokenError, InvalidTokenError
from src.utils.jwt import encode_jwt, decode_jwt
from src.config import get_settings

settings = get_settings()


class AuthService:
    def create_access_token(self, data: Dict[str, Any]) -> str:
        return encode_jwt(
            data=data,
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        return encode_jwt(
            data=data,
            secret_key=settings.refresh_secret_key,
            algorithm=settings.algorithm,
            expires_delta=timedelta(days=settings.refresh_token_expire_days),
        )

    def decode_access_token(self, token: str) -> Dict[str, Any]:
        try:
            return decode_jwt(token, settings.secret_key, settings.algorithm)
        except JWTError as e:
            if "Signature has expired" in str(e):
                raise ExpiredTokenError("Access token expired")
            raise InvalidTokenError("Invalid access token")

    def decode_refresh_token(self, token: str) -> Dict[str, Any]:
        try:
            return decode_jwt(token, settings.refresh_secret_key, settings.algorithm)
        except JWTError as e:
            if "Signature has expired" in str(e):
                raise ExpiredTokenError("Refresh token expired")
            raise InvalidTokenError("Invalid refresh token")


auth_service = AuthService()
