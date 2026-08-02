"""
Pydantic schemas: request/response validation, deliberately SEPARATE from
the SQLAlchemy model in models/user.py.

Why separate: the DB model has fields that should NEVER leave the server
(hashed_password). Mixing DB models and API schemas is a classic way to
accidentally leak a password hash in an API response. Keeping them
distinct means the response schema simply doesn't have that field --
it's structurally impossible to leak it, not just a matter of remembering
to exclude it.
"""

import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.STUDENT

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        """
        Enforce a minimum bar: 8+ characters, at least one letter and one
        number. This is intentionally simple -- strict enough to block
        trivially weak passwords ("12345678") without being so strict it
        frustrates users during a student project demo.
        """
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Za-z]", value):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one number")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """What we send BACK to the client -- notice: no password field at all."""
    id: int
    email: str
    full_name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True  # allows creating this directly from a SQLAlchemy User object


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
