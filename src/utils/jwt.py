from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from jose import jwt


def encode_jwt(
    data: Dict[str, Any], secret_key: str, algorithm: str, expires_delta: timedelta
) -> str:
    payload = data.copy()
    now = datetime.now(timezone.utc)
    payload["iat"] = now
    payload["exp"] = now + expires_delta
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_jwt(token: str, secret_key: str, algorithm: str) -> Dict[str, Any]:
    return jwt.decode(token, secret_key, algorithms=[algorithm])
