"""JWT token creation and validation."""

import os
import uuid
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def create_access_token(
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    papeis: list[str],
) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "papeis": papeis,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: uuid.UUID, tenant_id: uuid.UUID) -> str:
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Decode and validate a JWT token. Returns payload or None if invalid."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
