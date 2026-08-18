"""
Auth service: business logic for registration and login.

Kept separate from api/v1/routes/auth.py (route handlers) deliberately --
this is the "services" pattern mentioned in Module 0's folder structure
explanation. Routes should stay thin (parse request -> call service ->
return response); business logic lives here where it's testable without
spinning up the HTTP layer at all.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import PasswordResetToken, User
from app.schemas.user import UserLogin, UserRegister, UserUpdate


class AuthError(Exception):
    """Raised for any auth failure (duplicate email, wrong password, etc.)."""
    pass


def register_user(db: Session, user_data: UserRegister) -> User:
    if user_data.role and str(user_data.role.value).lower() == "admin" and user_data.email.lower().strip() != "dilipkumar.77b@gmail.com":
        raise AuthError("Admin registration is restricted. Only authorized system administrator accounts can hold the Admin role.")

    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise AuthError("An account with this email already exists")

    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role.value,
        institution=user_data.institution,
        department=user_data.department,
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


def create_password_reset_token(db: Session, email: str) -> str | None:
    """
    Generate a secure reset token if user exists.
    Returns raw token string if user exists, or None if user does not exist
    (calling route uses this to avoid account enumeration).
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    # Invalidate previous unused reset tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False
    ).update({"used": True})

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=30)

    reset_record = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        used=False
    )
    db.add(reset_record)
    db.commit()
    return raw_token


def validate_reset_token(db: Session, token: str) -> PasswordResetToken:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used == False
    ).first()

    if not reset_record:
        raise AuthError("Invalid or already used password reset token")

    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    if reset_record.expires_at < now_naive:
        raise AuthError("Password reset token has expired")

    return reset_record


def reset_password_with_token(db: Session, token: str, new_password: str) -> User:
    reset_record = validate_reset_token(db, token)
    user = db.query(User).filter(User.id == reset_record.user_id).first()
    if not user:
        raise AuthError("Associated user account not found")

    user.hashed_password = hash_password(new_password)
    reset_record.used = True
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(db: Session, user: User, update_data: UserUpdate) -> User:
    if update_data.full_name is not None and update_data.full_name.strip():
        user.full_name = update_data.full_name.strip()
    if update_data.role is not None:
        user.role = update_data.role.value
    if update_data.institution is not None:
        user.institution = update_data.institution.strip()
    if update_data.department is not None:
        user.department = update_data.department.strip()
    db.commit()
    db.refresh(user)
    return user


