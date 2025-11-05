"""
Authentication endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    name: Optional[str] = None


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    User login endpoint
    Returns access and refresh tokens
    """
    from ...security.auth import AuthManager
    from ...security.audit_logger import get_audit_logger
    
    # This is a placeholder - in production, verify against database
    # For now, just demonstrate the authentication flow
    
    logger.info(f"Login attempt for {request.email}")
    
    # Placeholder: Check credentials (replace with actual DB check)
    # For demo, accept any login with password length >= 8
    if len(request.password) < 8:
        get_audit_logger().log_login(
            user_id=request.email,
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create tokens
    auth_manager = AuthManager()
    user_data = {
        "sub": request.email,
        "email": request.email,
        "role": "user"
    }
    
    access_token = auth_manager.create_access_token(user_data)
    refresh_token = auth_manager.create_refresh_token(user_data)
    
    # Audit log
    get_audit_logger().log_login(
        user_id=request.email,
        success=True
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh access token using refresh token
    """
    from ...security.auth import AuthManager
    
    auth_manager = AuthManager()
    
    # Get new access token
    new_access_token = auth_manager.refresh_access_token(credentials.credentials)
    
    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=credentials.credentials  # Keep same refresh token
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user information
    """
    from ...security.auth import verify_token
    
    payload = verify_token(credentials.credentials)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return UserResponse(
        id=payload.get("sub", ""),
        email=payload.get("email", ""),
        name=payload.get("name")
    )


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get current user from token
    Can be used in other endpoints
    """
    from ...security.auth import verify_token
    
    payload = verify_token(credentials.credentials)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return payload
