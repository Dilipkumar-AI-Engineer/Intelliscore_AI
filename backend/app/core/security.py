"""
Security primitives: password hashing (bcrypt) and JWT tokens.

Concept -- why bcrypt, not just storing a hash: bcrypt is deliberately
SLOW (it includes a configurable "cost factor" of internal rounds). This
is a feature, not a bug -- it makes brute-forcing stolen password hashes
computationally expensive, unlike a fast general-purpose hash like SHA-256
(which is designed for speed, making it BAD for passwords specifically).

Concept -- JWT: a JSON Web Token is a signed (not encrypted) blob
containing claims (e.g. "user_id=5, expires=<timestamp>"). The signature
(created with JWT_SECRET_KEY) proves the token wasn't tampered with --
anyone can READ a JWT's contents (it's just base64), but only the server,
holding the secret key, can produce a validly SIGNED one. This is what
lets the server trust a token presented by the client without a database
lookup on every request (the signature check is enough).
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(subject: str) -> str:
    """
    Create a signed JWT. `subject` (the "sub" claim) is conventionally
    the user's unique identifier -- we use their email here.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """
    Verify and decode a JWT. Returns the subject (email) if valid, or
    None if the token is invalid, tampered with, or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return payload.get("sub")
    except JWTError:
        return None
