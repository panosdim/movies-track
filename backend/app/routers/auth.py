"""Authentication router for user registration and login."""

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import AppUser
from app.schemas.auth import RegisterRequest, LoginRequest, LoginResponse
from app.utils.password import hash_password, verify_password
from app.utils.jwt_token import create_access_token
from app.utils.security import get_current_user_email

router = APIRouter(tags=["auth"])


@router.post("/register", status_code=204)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(AppUser).filter(AppUser.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = hash_password(request.password)
    new_user = AppUser(
        email=request.email,
        password=hashed_password,
        first_name=request.first_name,
        last_name=request.last_name,
    )
    db.add(new_user)
    db.commit()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login and return JWT token."""
    user = db.query(AppUser).filter(AppUser.email == request.email).first()

    if not user or not verify_password(request.password, user.password or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password",
        )

    # Create token
    token = create_access_token({"sub": user.email, "user_id": user.id})

    return LoginResponse(
        token=token,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )


@router.get("/me", response_model=LoginResponse)
def get_me(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Get current authenticated user info."""
    user_email = get_current_user_email(authorization)
    user = db.query(AppUser).filter(AppUser.email == user_email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    token = create_access_token({"sub": user.email, "user_id": user.id})
    return LoginResponse(
        token=token,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )
