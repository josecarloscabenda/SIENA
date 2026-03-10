"""Authentication middleware and FastAPI dependencies."""

import uuid
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.common.auth.jwt import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    """Authenticated user context available in every request."""

    user_id: uuid.UUID
    tenant_id: uuid.UUID
    papeis: list[str]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    """FastAPI dependency: extracts and validates JWT from Authorization header."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
        )

    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    return CurrentUser(
        user_id=uuid.UUID(payload["sub"]),
        tenant_id=uuid.UUID(payload["tenant_id"]),
        papeis=payload.get("papeis", []),
    )
