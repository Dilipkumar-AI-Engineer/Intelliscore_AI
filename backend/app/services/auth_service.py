"""
Auth service: business logic for registration and login.

Kept separate from api/v1/routes/auth.py (route handlers) deliberately --
this is the "services" pattern mentioned in Module 0's folder structure
explanation. Routes should stay thin (parse request -> call service ->
return response); business logic lives here where it's testable without
spinning up the HTTP layer at all.
"""

from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister


class AuthError(Exception):
    """Raised for any auth failure (duplicate email, wrong password, etc.)."""
    pass


def register_user(db: Session, user_data: UserRegister) -> User:
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise AuthError("An account with this email already exists")

    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, credentials: UserLogin) -> tuple[User, str]:
    """
    Verify credentials and return (user, access_token) on success.
    Raises AuthError on any failure. Deliberately uses the SAME error
    message for "no such email" and "wrong password" -- revealing which
    one was wrong ("email not found" vs "wrong password") lets an
    attacker enumerate valid registered emails, a real security leak.
    """
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise AuthError("Incorrect email or password")

    token = create_access_token(subject=user.email)
    return user, token
