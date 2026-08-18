"""
Auth routes. Deliberately thin -- each handler parses the request,
delegates to auth_service, and shapes the response. No business logic
lives here (see services/auth_service.py).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)
from app.services.auth_service import (
    AuthError,
    authenticate_user,
    create_password_reset_token,
    register_user,
    reset_password_with_token,
    update_user_profile,
    validate_reset_token,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        user = register_user(db, user_data)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    try:
        user, token = authenticate_user(db, credentials)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenResponse(access_token=token, user=user)


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    raw_token = create_password_reset_token(db, req.email)
    response_data = {
        "message": "If an account exists for this email, password reset instructions will be provided."
    }
    # In development mode, if user existed, include dev token for direct UI testing
    if raw_token:
        response_data["dev_reset_token"] = raw_token
        response_data["dev_reset_url"] = f"/reset-password?token={raw_token}"

    return response_data


@router.get("/verify-reset-token")
def verify_token(token: str, db: Session = Depends(get_db)):
    try:
        validate_reset_token(db, token)
        return {"valid": True, "message": "Token is valid"}
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        reset_password_with_token(db, req.token, req.new_password)
        return {"message": "Password has been reset successfully. You may now login."}
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Protected route: proves the JWT auth flow works end-to-end."""
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_current_user(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current logged-in user profile (full name, role, etc.)."""
    try:
        updated_user = update_user_profile(db, current_user, update_data)
        return updated_user
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all registered users (students, teachers, admins) with essay metrics."""
    user_role = (current_user.role or "student").lower()
    if user_role not in ["teacher", "admin", "administrator"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher or Admin role required.")

    users = db.query(User).all()
    from app.models.essay import Essay
    result = []
    for u in users:
        essay_count = db.query(Essay).filter(Essay.user_id == u.id).count()
        result.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "essay_count": essay_count,
        })
    return result


@router.patch("/users/{user_id}")
def update_user_by_admin(
    user_id: int,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin endpoint to update teacher or student profile information."""
    user_role = (current_user.role or "student").lower()
    if user_role not in ["admin", "administrator", "teacher"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Teacher role required.")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    try:
        updated_user = update_user_profile(db, target_user, update_data)
        return updated_user
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



