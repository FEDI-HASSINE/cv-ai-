"""
Authentication and Authorization Module
Implements JWT-based authentication for API access
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class AuthManager:
    """
    Authentication manager for user authentication and JWT tokens
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize authentication manager
        
        Args:
            secret_key: JWT secret key. If None, gets from secrets manager
        """
        if secret_key:
            self.secret_key = secret_key
        else:
            from .secrets_manager import get_secrets_manager
            secrets_mgr = get_secrets_manager()
            self.secret_key = secrets_mgr.get_jwt_secret()
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Data to encode in token (usually user_id, email, roles)
            expires_delta: Optional expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation error: {e}")
            raise ValueError("Failed to create access token")
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT refresh token (longer expiration)
        
        Args:
            data: Data to encode in token
            
        Returns:
            JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Refresh token creation error: {e}")
            raise ValueError("Failed to create refresh token")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token data if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if a token is expired
        
        Args:
            token: JWT token string
            
        Returns:
            True if expired or invalid, False if valid
        """
        payload = self.verify_token(token)
        if not payload:
            return True
        
        exp = payload.get("exp")
        if not exp:
            return True
        
        return datetime.fromtimestamp(exp) < datetime.utcnow()
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Generate new access token from refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token if refresh token is valid, None otherwise
        """
        payload = self.verify_token(refresh_token)
        
        if not payload:
            return None
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            logger.warning("Attempted to use non-refresh token for refresh")
            return None
        
        # Create new access token with same data (minus token-specific fields)
        token_data = {k: v for k, v in payload.items() 
                     if k not in ["exp", "iat", "type"]}
        
        return self.create_access_token(token_data)


# Convenience functions
def create_access_token(data: Dict[str, Any], secret_key: Optional[str] = None) -> str:
    """
    Convenience function to create access token
    
    Args:
        data: Data to encode
        secret_key: Optional secret key
        
    Returns:
        JWT access token
    """
    auth_manager = AuthManager(secret_key)
    return auth_manager.create_access_token(data)


def verify_token(token: str, secret_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Convenience function to verify token
    
    Args:
        token: JWT token
        secret_key: Optional secret key
        
    Returns:
        Decoded payload if valid, None otherwise
    """
    auth_manager = AuthManager(secret_key)
    return auth_manager.verify_token(token)


def hash_password(password: str) -> str:
    """
    Convenience function to hash password
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Convenience function to verify password
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)
