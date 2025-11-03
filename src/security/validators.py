"""
Input validation and sanitization utilities
Prevents injection attacks and validates user inputs
"""

import re
from typing import Optional, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Input validation and sanitization for security
    """
    
    # Common patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{1,14}$')  # E.164 format
    
    # Dangerous patterns for SQL/NoSQL injection
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"('|\")\s*(OR|AND)\s*('|\").*=.*('|\")",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
    ]
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not email or len(email) > 254:  # Max email length
            return False
        return bool(InputValidator.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
        """
        Validate URL format
        
        Args:
            url: URL to validate
            allowed_schemes: List of allowed schemes (default: ['http', 'https'])
            
        Returns:
            True if valid, False otherwise
        """
        if not url:
            return False
        
        allowed_schemes = allowed_schemes or ['http', 'https']
        
        # Check basic format
        if not InputValidator.URL_PATTERN.match(url):
            return False
        
        # Check scheme
        scheme = url.split('://')[0].lower()
        return scheme in allowed_schemes
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone number (E.164 format)
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not phone:
            return False
        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        return bool(InputValidator.PHONE_PATTERN.match(cleaned))
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return "unnamed"
        
        # Remove path separators and dangerous characters
        filename = Path(filename).name
        filename = re.sub(r'[^\w\s\-\.]', '', filename)
        filename = re.sub(r'\.\.+', '.', filename)  # Remove multiple dots
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename or "unnamed"
    
    @staticmethod
    def check_sql_injection(text: str) -> bool:
        """
        Check for potential SQL injection patterns
        
        Args:
            text: Text to check
            
        Returns:
            True if suspicious patterns found, False otherwise
        """
        if not text:
            return False
        
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {pattern}")
                return True
        
        return False
    
    @staticmethod
    def check_xss(text: str) -> bool:
        """
        Check for potential XSS patterns
        
        Args:
            text: Text to check
            
        Returns:
            True if suspicious patterns found, False otherwise
        """
        if not text:
            return False
        
        for pattern in InputValidator.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential XSS detected: {pattern}")
                return True
        
        return False
    
    @staticmethod
    def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize text input
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newline, tab, carriage return
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Limit length
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text.strip()
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """
        Validate file extension
        
        Args:
            filename: Filename to check
            allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.docx'])
            
        Returns:
            True if valid, False otherwise
        """
        if not filename:
            return False
        
        ext = Path(filename).suffix.lower()
        return ext in [e.lower() for e in allowed_extensions]
    
    @staticmethod
    def validate_file_size(file_size_bytes: int, max_size_mb: int = 10) -> bool:
        """
        Validate file size
        
        Args:
            file_size_bytes: File size in bytes
            max_size_mb: Maximum allowed size in MB
            
        Returns:
            True if valid, False otherwise
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        return 0 < file_size_bytes <= max_size_bytes
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validate username format
        
        Args:
            username: Username to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not username or len(username) < 3 or len(username) > 50:
            return False
        
        # Allow alphanumeric, underscore, hyphen
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', username))
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if len(password) > 128:
            return False, "Password is too long (max 128 characters)"
        
        # Check for at least one uppercase, lowercase, digit, and special char
        checks = [
            (r'[A-Z]', "uppercase letter"),
            (r'[a-z]', "lowercase letter"),
            (r'\d', "digit"),
            (r'[!@#$%^&*(),.?":{}|<>]', "special character")
        ]
        
        for pattern, requirement in checks:
            if not re.search(pattern, password):
                return False, f"Password must contain at least one {requirement}"
        
        return True, "Password is strong"


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Convenience function for input sanitization
    
    Args:
        text: Text to sanitize
        max_length: Maximum length
        
    Returns:
        Sanitized text
    """
    validator = InputValidator()
    
    # Check for injection attempts
    if validator.check_sql_injection(text):
        logger.warning("SQL injection attempt blocked")
        return ""
    
    if validator.check_xss(text):
        logger.warning("XSS attempt blocked")
        return ""
    
    # Sanitize
    return validator.sanitize_text(text, max_length)
