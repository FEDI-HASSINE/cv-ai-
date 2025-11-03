"""
Secrets Manager - Enhanced security for sensitive data
Manages API keys, tokens, and sensitive configuration securely
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Centralized secrets management with validation and security best practices
    Supports environment variables, .env files, and future integration with 
    HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault
    """
    
    def __init__(self, env_file: Optional[Path] = None):
        """
        Initialize secrets manager
        
        Args:
            env_file: Path to .env file (default: .env in project root)
        """
        self.env_file = env_file or Path(__file__).parent.parent.parent / ".env"
        self._secrets_cache: Dict[str, str] = {}
        self._load_environment()
        
    def _load_environment(self):
        """Load environment variables with validation"""
        try:
            # Try to load python-dotenv if available
            try:
                from dotenv import load_dotenv
                if self.env_file.exists():
                    load_dotenv(self.env_file)
                    logger.info(f"Loaded environment from {self.env_file}")
                else:
                    logger.warning(f"Environment file not found: {self.env_file}")
            except ImportError:
                logger.warning("python-dotenv not installed, using system environment only")
        except Exception as e:
            logger.error(f"Error loading environment: {e}")
    
    def get_secret(self, key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
        """
        Safely retrieve a secret with validation
        
        Args:
            key: Secret key name
            default: Default value if not found
            required: Raise error if not found and no default
            
        Returns:
            Secret value or default
            
        Raises:
            ValueError: If required=True and secret not found
        """
        # Check cache first
        if key in self._secrets_cache:
            return self._secrets_cache[key]
        
        # Get from environment
        value = os.getenv(key, default)
        
        if value is None and required:
            raise ValueError(f"Required secret '{key}' not found in environment")
        
        # Cache non-None values
        if value is not None:
            self._secrets_cache[key] = value
        
        return value
    
    def validate_api_key(self, key: str) -> bool:
        """
        Validate API key format
        
        Args:
            key: API key to validate
            
        Returns:
            True if valid format, False otherwise
        """
        if not key:
            return False
        
        # Basic validation - should be alphanumeric with some special chars
        # At least 20 characters for security
        if len(key) < 20:
            return False
        
        # Check for obvious dummy values
        dummy_values = ['your_key_here', 'placeholder', 'example', 'test_key']
        if any(dummy in key.lower() for dummy in dummy_values):
            return False
        
        return True
    
    def get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key with validation"""
        key = self.get_secret("OPENAI_API_KEY")
        if key and not self.validate_api_key(key):
            logger.warning("OpenAI API key appears invalid")
            return None
        return key
    
    def get_github_token(self) -> Optional[str]:
        """Get GitHub token"""
        return self.get_secret("GITHUB_TOKEN")
    
    def get_stackoverflow_key(self) -> Optional[str]:
        """Get StackOverflow API key"""
        return self.get_secret("STACKOVERFLOW_KEY")
    
    def get_database_url(self) -> Optional[str]:
        """Get database connection string"""
        return self.get_secret("DATABASE_URL")
    
    def get_redis_url(self) -> Optional[str]:
        """Get Redis connection string"""
        return self.get_secret("REDIS_URL")
    
    def get_jwt_secret(self) -> str:
        """
        Get JWT secret key
        Generates a secure one if not set (for development only)
        """
        secret = self.get_secret("JWT_SECRET")
        if not secret:
            logger.warning("JWT_SECRET not set, generating temporary key (NOT FOR PRODUCTION)")
            import secrets
            secret = secrets.token_urlsafe(32)
        return secret
    
    def get_encryption_key(self) -> bytes:
        """
        Get or generate encryption key for file encryption
        In production, this should come from a secure key management service
        """
        key_str = self.get_secret("ENCRYPTION_KEY")
        
        if not key_str:
            logger.warning("ENCRYPTION_KEY not set, generating temporary key (NOT FOR PRODUCTION)")
            from cryptography.fernet import Fernet
            key = Fernet.generate_key()
            return key
        
        # Convert from base64 string to bytes
        import base64
        try:
            return base64.b64decode(key_str.encode())
        except Exception as e:
            logger.error(f"Invalid encryption key format: {e}")
            from cryptography.fernet import Fernet
            return Fernet.generate_key()
    
    def mask_secret(self, secret: str, visible_chars: int = 4) -> str:
        """
        Mask a secret for logging purposes
        
        Args:
            secret: Secret to mask
            visible_chars: Number of characters to show at end
            
        Returns:
            Masked string (e.g., "****xyz123")
        """
        if not secret or len(secret) <= visible_chars:
            return "****"
        
        return "*" * (len(secret) - visible_chars) + secret[-visible_chars:]
    
    def rotate_key(self, key_name: str) -> bool:
        """
        Placeholder for key rotation functionality
        In production, this would integrate with key management services
        
        Args:
            key_name: Name of key to rotate
            
        Returns:
            True if successful
        """
        logger.info(f"Key rotation requested for: {key_name}")
        # Clear from cache to force reload
        if key_name in self._secrets_cache:
            del self._secrets_cache[key_name]
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check health of secrets configuration
        
        Returns:
            Dict with status of various secrets
        """
        return {
            "openai_configured": bool(self.get_openai_key()),
            "github_configured": bool(self.get_github_token()),
            "stackoverflow_configured": bool(self.get_stackoverflow_key()),
            "database_configured": bool(self.get_database_url()),
            "redis_configured": bool(self.get_redis_url()),
            "jwt_configured": bool(self.get_secret("JWT_SECRET")),
            "encryption_configured": bool(self.get_secret("ENCRYPTION_KEY"))
        }


# Global instance
_secrets_manager = None


def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager instance"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager
