"""
Auth dependency: extracts and validates the current user from the
Authorization header. Any route that needs to be "logged in only" simply
adds `current_user: User = Depends(get_current_user)` as a parameter --
FastAPI runs this automatically before the route body executes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

# tokenUrl is documentation-only here (points Swagger UI's "Authorize"
# button at our login route) -- it doesn't change how token validation works.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


def require_role(allowed_roles: list[str]):
    """Dependency generator to restrict route access to specific roles."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = (current_user.role or "").lower()
        normalized_allowed = [r.lower() for r in allowed_roles]
        if "admin" in normalized_allowed and "administrator" not in normalized_allowed:
            normalized_allowed.append("administrator")
        if user_role not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: User role '{user_role}' is not authorized for this operation.",
            )
        return current_user
    return role_checker
