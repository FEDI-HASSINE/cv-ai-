# Security Implementation Guide

## Overview

This document describes the security enhancements implemented in UtopiaHire following the technical review recommendations.

## Security Modules Implemented

### 1. Secrets Management (`src/security/secrets_manager.py`)

**Purpose**: Centralized, secure management of API keys, tokens, and sensitive configuration.

**Features**:
- Environment-based secrets loading with validation
- API key format validation
- Secret masking for logging
- Health check for configuration status
- Key rotation support (placeholder for production integration)
- Ready for integration with HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault

**Usage**:
```python
from src.security.secrets_manager import get_secrets_manager

secrets = get_secrets_manager()
api_key = secrets.get_openai_key()
jwt_secret = secrets.get_jwt_secret()
```

**Security Best Practices**:
- Never commit `.env` file to version control
- Use strong, unique keys for production
- Rotate keys regularly
- Monitor secret access through audit logs

### 2. File Encryption (`src/security/encryption.py`)

**Purpose**: Secure storage of uploaded CV documents using AES encryption.

**Features**:
- Fernet symmetric encryption (AES-128 in CBC mode)
- File and data encryption/decryption
- Secure key generation and storage
- Automatic cleanup of temporary files

**Usage**:
```python
from src.security.encryption import encrypt_file, decrypt_file

# Encrypt a CV
encrypted_path = encrypt_file("resume.pdf")

# Decrypt when needed
decrypted_path = decrypt_file("resume.pdf.enc")
```

**Security Best Practices**:
- Generate unique encryption keys per deployment
- Store encryption keys in secure key management service
- Set restrictive file permissions (0600) on key files
- Delete decrypted files after use

### 3. Authentication & Authorization (`src/security/auth.py`)

**Purpose**: JWT-based authentication for API access with password hashing.

**Features**:
- JWT access and refresh tokens
- Bcrypt password hashing
- Token verification and expiration
- Token refresh mechanism
- Configurable token expiration times

**Usage**:
```python
from src.security.auth import AuthManager

auth = AuthManager()

# Hash password
hashed = auth.hash_password("user_password")

# Create tokens
access_token = auth.create_access_token({"sub": "user@example.com"})

# Verify token
payload = auth.verify_token(access_token)
```

**Security Best Practices**:
- Use strong JWT secrets (32+ bytes)
- Set appropriate token expiration times
- Implement token revocation for logout
- Use HTTPS only in production
- Store tokens securely on client side

### 4. Input Validation (`src/security/validators.py`)

**Purpose**: Prevent injection attacks and validate user inputs.

**Features**:
- SQL injection detection
- XSS (Cross-Site Scripting) detection
- Email, URL, phone validation
- Filename sanitization (prevents directory traversal)
- File size and extension validation
- Password strength validation
- Input sanitization

**Usage**:
```python
from src.security.validators import InputValidator, sanitize_input

validator = InputValidator()

# Validate inputs
if validator.check_sql_injection(user_input):
    # Block request
    pass

# Sanitize
safe_text = sanitize_input(user_input)
safe_filename = validator.sanitize_filename(upload.filename)
```

**Security Best Practices**:
- Always validate and sanitize user inputs
- Use allowlists over denylists when possible
- Limit input lengths
- Validate file types by content, not just extension

### 5. Audit Logging (`src/security/audit_logger.py`)

**Purpose**: Track security-related events for monitoring and compliance.

**Features**:
- Structured JSON logging
- Event types: login, logout, file access, API calls, security alerts
- Failed login tracking
- User activity tracking
- Searchable audit trail

**Usage**:
```python
from src.security.audit_logger import get_audit_logger

audit = get_audit_logger()

# Log events
audit.log_login(user_id="user@example.com", success=True, ip_address="1.2.3.4")
audit.log_file_upload(user_id="user@example.com", filename="resume.pdf", 
                      file_size=1024000, success=True)

# Query logs
failed_logins = audit.get_failed_logins(hours=24)
```

**Security Best Practices**:
- Enable audit logging in production
- Monitor failed login attempts
- Set up alerts for suspicious activity
- Retain logs for compliance requirements (e.g., 90+ days)
- Protect log files with appropriate permissions

## FastAPI Backend Security

### API Security Features

1. **Security Headers**: Automatic injection of security headers (CSP, XSS protection, etc.)
2. **Rate Limiting**: 60 requests per minute per IP (configurable)
3. **CORS**: Restricted to allowed origins
4. **Request Logging**: All API requests logged with timing
5. **JWT Authentication**: Protected endpoints require valid tokens

### Middleware Stack

```python
# Security headers
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
```

### Running the API

```bash
# Development
uvicorn src.api.main:app --reload --port 8000

# Production (with Gunicorn)
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### API Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/resume/analyze` - Analyze resume
- `POST /api/v1/jobs/search` - Search jobs
- `POST /api/v1/jobs/match` - Match candidate to jobs

## Environment Configuration

### Required Environment Variables

```bash
# Security (CRITICAL)
JWT_SECRET=<generate-with-secrets.token_urlsafe(32)>
ENCRYPTION_KEY=<generate-with-Fernet.generate_key()>
SECRET_KEY=<generate-strong-key>

# Optional API Keys
OPENAI_API_KEY=<your-key>
GITHUB_TOKEN=<your-token>
STACKOVERFLOW_KEY=<your-key>

# Database (when configured)
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379/0
```

### Generating Secure Keys

```bash
# JWT Secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Encryption Key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Production Deployment Checklist

### Before Deploying

- [ ] Generate and set all secret keys in production `.env`
- [ ] Set `DEBUG=False`
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up proper database with strong credentials
- [ ] Configure firewall rules (allow only 80, 443, SSH)
- [ ] Enable audit logging
- [ ] Set up monitoring (Prometheus, Grafana, etc.)
- [ ] Configure log rotation
- [ ] Set up backup strategy for encryption keys
- [ ] Review and restrict CORS origins
- [ ] Set up rate limiting per user (not just IP)
- [ ] Configure secret rotation schedule
- [ ] Enable database connection encryption
- [ ] Set up intrusion detection
- [ ] Configure automated security updates

### During Deployment

- [ ] Use environment variables (not files) for secrets
- [ ] Deploy behind reverse proxy (Nginx, Traefik)
- [ ] Enable HTTP/2 and TLS 1.3
- [ ] Configure security headers
- [ ] Set up DDoS protection (Cloudflare, AWS Shield)
- [ ] Enable database backups
- [ ] Configure file upload limits

### After Deployment

- [ ] Test authentication flows
- [ ] Verify rate limiting works
- [ ] Check audit logs are being written
- [ ] Test file encryption/decryption
- [ ] Verify all endpoints require authentication
- [ ] Run security scan (OWASP ZAP, Burp Suite)
- [ ] Perform penetration testing
- [ ] Set up alert notifications
- [ ] Document incident response procedures

## Security Monitoring

### Metrics to Monitor

1. **Failed login attempts** - Alert if > 5 from same IP in 5 minutes
2. **API response times** - Alert if average > 1s
3. **Error rates** - Alert if > 1% of requests
4. **Disk space** - Alert if logs directory > 80% full
5. **Database connections** - Alert if connection pool exhausted
6. **Rate limit violations** - Track and alert on patterns

### Log Monitoring

```bash
# View audit log
tail -f logs/audit.log | jq

# Find failed logins in last hour
jq 'select(.event_type == "auth_failed")' logs/audit.log

# Count requests by endpoint
jq -r '.details.endpoint' logs/audit.log | sort | uniq -c
```

## Security Testing

### Testing Tools

1. **OWASP ZAP** - Automated security testing
2. **Burp Suite** - Manual security testing
3. **SQLMap** - SQL injection testing
4. **XSStrike** - XSS vulnerability testing
5. **Safety** - Python dependency vulnerability scanner

### Running Security Tests

```bash
# Check for vulnerable dependencies
pip install safety
safety check

# Run pytest with security tests
pytest tests/security/
```

## Compliance

### GDPR Considerations

- [ ] Implement right to erasure (delete user data)
- [ ] Implement data portability (export user data)
- [ ] Document data processing activities
- [ ] Implement consent management
- [ ] Configure data retention policies
- [ ] Enable encryption at rest and in transit
- [ ] Document breach notification procedures

### Industry Standards

- **OWASP Top 10**: Address common vulnerabilities
- **PCI DSS**: If handling payment data
- **SOC 2**: For service organizations
- **ISO 27001**: Information security management

## Incident Response

### In Case of Security Breach

1. **Immediate Actions**:
   - Isolate affected systems
   - Revoke compromised credentials
   - Enable additional logging

2. **Investigation**:
   - Review audit logs
   - Identify scope of breach
   - Document timeline

3. **Remediation**:
   - Patch vulnerabilities
   - Rotate all secrets
   - Update security measures

4. **Communication**:
   - Notify affected users
   - Report to authorities (if required)
   - Document lessons learned

## Support & Contact

For security issues or questions:
- Email: security@utopiahire.com (create this)
- Security Policy: See SECURITY.md
- Bug Bounty Program: (if implemented)

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
