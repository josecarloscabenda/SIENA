"""Role-Based Access Control (RBAC) dependencies."""

from fastapi import Depends, HTTPException, status
from src.common.auth.middleware import CurrentUser, get_current_user


def require_role(*allowed_roles: str):
    """FastAPI dependency factory: requires the user to have at least one of the specified roles.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("super_admin", "diretor"))])
    """

    async def check_role(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not any(role in user.papeis for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Papéis requeridos: {', '.join(allowed_roles)}",
            )
        return user

    return check_role
