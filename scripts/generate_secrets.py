#!/usr/bin/env python3
"""
Generate secure secrets for UtopiaHire production deployment

SECURITY NOTE: This script intentionally outputs secrets to console and file
for initial setup purposes. The generated secrets should be:
1. Immediately copied to .env file
2. The .secrets file should be deleted after copying
3. Never committed to version control
4. Kept secure and backed up separately
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
    print("⚠️  WARNING: The secrets displayed below are sensitive!")
    print("⚠️  Ensure your terminal is not being recorded/shared")
    print()
    
    # Generate JWT secret
    jwt_secret = secrets.token_urlsafe(32)
    # CodeQL: Intentional cleartext logging for initial setup
    print("JWT_SECRET (for authentication):")
    print(jwt_secret)
    print()
    
    # Generate encryption key
    encryption_key = Fernet.generate_key().decode()
    # CodeQL: Intentional cleartext logging for initial setup
    print("ENCRYPTION_KEY (for file encryption):")
    print(encryption_key)
    print()
    
    # Generate general secret key
    secret_key = secrets.token_urlsafe(32)
    print("SECRET_KEY (for general app security):")
    print(secret_key)
    print()
    
    # Save to file (will be deleted after copying to .env)
    secrets_file = Path(__file__).parent.parent / ".secrets"
    
    # CodeQL: Intentional cleartext storage for initial setup only
    with open(secrets_file, 'w') as f:
        f.write("# Generated secrets - DO NOT COMMIT TO VERSION CONTROL\n")
        f.write("# Copy these values to your .env file and DELETE THIS FILE\n\n")
        f.write(f"JWT_SECRET={jwt_secret}\n")
        f.write(f"ENCRYPTION_KEY={encryption_key}\n")
        f.write(f"SECRET_KEY={secret_key}\n")
    
    # Set restrictive permissions
    import os
    os.chmod(secrets_file, 0o600)  # Only owner can read/write
    
    print(f"Secrets saved to: {secrets_file}")
    print(f"File permissions set to 0600 (owner read/write only)")
    print()
    print("=" * 60)
    print("IMPORTANT SECURITY STEPS:")
    print("=" * 60)
    print("1. Copy these values to your .env file IMMEDIATELY")
    print("2. DELETE the .secrets file after copying:")
    print(f"   rm {secrets_file}")
    print("3. NEVER commit these secrets to version control")
    print("4. Keep them secure and backed up separately")
    print("5. For production, consider using a secret manager:")
    print("   - HashiCorp Vault")
    print("   - AWS Secrets Manager")
    print("   - Azure Key Vault")
    print("=" * 60)


if __name__ == "__main__":
    generate_secrets()
