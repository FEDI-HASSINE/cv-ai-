#!/usr/bin/env python3
"""
Generate secure secrets for UtopiaHire production deployment
"""

import secrets
from cryptography.fernet import Fernet
from pathlib import Path


def generate_secrets():
    """Generate all required secrets"""
    
    print("=" * 60)
    print("UtopiaHire Secret Generator")
    print("=" * 60)
    print()
    
    # Generate JWT secret
    jwt_secret = secrets.token_urlsafe(32)
    print("JWT_SECRET (for authentication):")
    print(jwt_secret)
    print()
    
    # Generate encryption key
    encryption_key = Fernet.generate_key().decode()
    print("ENCRYPTION_KEY (for file encryption):")
    print(encryption_key)
    print()
    
    # Generate general secret key
    secret_key = secrets.token_urlsafe(32)
    print("SECRET_KEY (for general app security):")
    print(secret_key)
    print()
    
    # Save to file
    secrets_file = Path(__file__).parent.parent / ".secrets"
    
    with open(secrets_file, 'w') as f:
        f.write("# Generated secrets - DO NOT COMMIT TO VERSION CONTROL\n")
        f.write("# Copy these values to your .env file\n\n")
        f.write(f"JWT_SECRET={jwt_secret}\n")
        f.write(f"ENCRYPTION_KEY={encryption_key}\n")
        f.write(f"SECRET_KEY={secret_key}\n")
    
    print(f"Secrets saved to: {secrets_file}")
    print()
    print("IMPORTANT:")
    print("1. Copy these values to your .env file")
    print("2. Delete the .secrets file after copying")
    print("3. Never commit these secrets to version control")
    print("4. Keep them secure and backed up separately")
    print()
    print("=" * 60)


if __name__ == "__main__":
    generate_secrets()
