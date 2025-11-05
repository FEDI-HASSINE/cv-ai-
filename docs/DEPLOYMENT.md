# Deployment Guide

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+ (optional, SQLite fallback available)
- Redis (optional, for Celery)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/FEDI-HASSINE/cv-ai-.git
cd cv-ai-

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your configuration

# 5. Generate secrets (IMPORTANT!)
python scripts/generate_secrets.py

# 6. Initialize database (optional, auto-creates SQLite if not configured)
python -c "from src.database import create_tables; create_tables()"

# 7. Run the application
streamlit run app.py
```

### Running the API

```bash
# Development mode
uvicorn src.api.main:app --reload --port 8000

# Visit: http://localhost:8000/api/docs
```

## Production Deployment

### Server Requirements

- **CPU**: 2+ cores
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB+ (for job database and logs)
- **OS**: Ubuntu 20.04+ or similar Linux distribution

### Step-by-Step Production Setup

#### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.10 python3.10-venv python3-pip \
    postgresql postgresql-contrib redis-server nginx \
    certbot python3-certbot-nginx git

# Create application user
sudo useradd -m -s /bin/bash utopiahire
sudo usermod -aG sudo utopiahire
```

#### 2. PostgreSQL Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE utopiahire;
CREATE USER utopiahire_user WITH ENCRYPTED PASSWORD 'CHANGE_THIS_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE utopiahire TO utopiahire_user;
\q

# Test connection
psql -h localhost -U utopiahire_user -d utopiahire
```

#### 3. Application Setup

```bash
# Switch to app user
sudo su - utopiahire

# Clone and setup
git clone https://github.com/FEDI-HASSINE/cv-ai-.git
cd cv-ai-
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Generate secrets
python scripts/generate_secrets.py

# Configure environment
cp .env.example .env
nano .env  # Edit configuration
```

#### 4. Environment Configuration

Edit `.env`:

```bash
# Production settings
DEBUG=False
APP_ENV=production

# Database
DATABASE_URL=postgresql://utopiahire_user:PASSWORD@localhost:5432/utopiahire

# Redis
REDIS_URL=redis://localhost:6379/0

# Security (use values from generate_secrets.py)
JWT_SECRET=<generated-secret>
ENCRYPTION_KEY=<generated-key>
SECRET_KEY=<generated-key>

# API Keys (add your own)
OPENAI_API_KEY=<your-key>
GITHUB_TOKEN=<your-token>
```

#### 5. Initialize Database

```bash
python -c "from src.database import create_tables; create_tables()"
```

#### 6. Setup Systemd Services

**API Service** (`/etc/systemd/system/utopiahire-api.service`):

```ini
[Unit]
Description=UtopiaHire API
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=utopiahire
Group=utopiahire
WorkingDirectory=/home/utopiahire/cv-ai-
Environment="PATH=/home/utopiahire/cv-ai-/venv/bin"
ExecStart=/home/utopiahire/cv-ai-/venv/bin/gunicorn src.api.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile /home/utopiahire/cv-ai-/logs/access.log \
    --error-logfile /home/utopiahire/cv-ai-/logs/error.log

[Install]
WantedBy=multi-user.target
```

**Celery Worker** (`/etc/systemd/system/utopiahire-celery.service`):

```ini
[Unit]
Description=UtopiaHire Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=utopiahire
Group=utopiahire
WorkingDirectory=/home/utopiahire/cv-ai-
Environment="PATH=/home/utopiahire/cv-ai-/venv/bin"
ExecStart=/home/utopiahire/cv-ai-/venv/bin/celery -A src.automation.tasks worker \
    --loglevel=info \
    --logfile=/home/utopiahire/cv-ai-/logs/celery.log \
    --detach

[Install]
WantedBy=multi-user.target
```

**Celery Beat** (`/etc/systemd/system/utopiahire-beat.service`):

```ini
[Unit]
Description=UtopiaHire Celery Beat
After=network.target redis.service

[Service]
Type=forking
User=utopiahire
Group=utopiahire
WorkingDirectory=/home/utopiahire/cv-ai-
Environment="PATH=/home/utopiahire/cv-ai-/venv/bin"
ExecStart=/home/utopiahire/cv-ai-/venv/bin/celery -A src.automation.tasks beat \
    --loglevel=info \
    --logfile=/home/utopiahire/cv-ai-/logs/celery-beat.log \
    --detach

[Install]
WantedBy=multi-user.target
```

#### 7. Start Services

```bash
# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable utopiahire-api
sudo systemctl enable utopiahire-celery
sudo systemctl enable utopiahire-beat

sudo systemctl start utopiahire-api
sudo systemctl start utopiahire-celery
sudo systemctl start utopiahire-beat

# Check status
sudo systemctl status utopiahire-api
sudo systemctl status utopiahire-celery
sudo systemctl status utopiahire-beat
```

#### 8. Nginx Configuration

Create `/etc/nginx/sites-available/utopiahire`:

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=app_limit:10m rate=30r/s;

# Upstream API
upstream utopiahire_api {
    server 127.0.0.1:8000;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API endpoint
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://utopiahire_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # File upload size
    client_max_body_size 10M;

    # Logging
    access_log /var/log/nginx/utopiahire_access.log;
    error_log /var/log/nginx/utopiahire_error.log;
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/utopiahire /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 9. SSL Certificate (Let's Encrypt)

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is set up by default, test with:
sudo certbot renew --dry-run
```

#### 10. Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# Check status
sudo ufw status
```

## Monitoring

### Log Locations

- **API logs**: `/home/utopiahire/cv-ai-/logs/`
- **Nginx logs**: `/var/log/nginx/`
- **System logs**: `journalctl -u utopiahire-api`

### Health Checks

```bash
# API health
curl https://yourdomain.com/api/v1/health

# Service status
sudo systemctl status utopiahire-api
sudo systemctl status utopiahire-celery
sudo systemctl status utopiahire-beat
```

### Monitoring Tools

Consider setting up:
- **Prometheus** + **Grafana** for metrics
- **ELK Stack** for log analysis
- **Sentry** for error tracking
- **Uptime Kuma** for uptime monitoring

## Backup Strategy

### Database Backup

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/home/utopiahire/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
pg_dump -U utopiahire_user utopiahire | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Keep last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

# Add to crontab:
# 0 2 * * * /home/utopiahire/scripts/backup.sh
```

### Application Backup

```bash
# Backup uploaded files and logs
tar -czf backups/files_$(date +%Y%m%d).tar.gz data/ logs/
```

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Add Nginx load balancer
2. **Multiple API instances**: Run on different ports/servers
3. **Database replication**: PostgreSQL primary-replica setup
4. **Redis cluster**: For distributed caching

### Vertical Scaling

1. **Increase workers**: Adjust Gunicorn `-w` parameter
2. **Database tuning**: Optimize PostgreSQL configuration
3. **Caching**: Implement Redis caching for frequently accessed data

## Troubleshooting

### Common Issues

**Issue**: API not starting
```bash
# Check logs
journalctl -u utopiahire-api -n 50

# Check if port is in use
sudo lsof -i :8000

# Test manually
cd /home/utopiahire/cv-ai-
source venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

**Issue**: Database connection failed
```bash
# Test PostgreSQL connection
psql -h localhost -U utopiahire_user -d utopiahire

# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string in .env
```

**Issue**: Celery tasks not running
```bash
# Check Celery worker
sudo systemctl status utopiahire-celery

# Check Redis
redis-cli ping

# Monitor tasks
celery -A src.automation.tasks inspect active
```

## Security Best Practices

1. **Keep software updated**: Regular system updates
2. **Strong passwords**: Use password managers
3. **Firewall**: Only allow necessary ports
4. **SSH keys**: Disable password authentication
5. **Fail2ban**: Protect against brute force attacks
6. **Regular backups**: Test restore procedures
7. **Monitor logs**: Set up alerts for suspicious activity
8. **Rate limiting**: Enforce API rate limits
9. **Input validation**: Always validate user inputs
10. **Security audits**: Regular penetration testing

## Update Procedure

```bash
# 1. Backup
./scripts/backup.sh

# 2. Pull updates
cd /home/utopiahire/cv-ai-
git pull origin main

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Run migrations (if any)
# alembic upgrade head

# 5. Restart services
sudo systemctl restart utopiahire-api
sudo systemctl restart utopiahire-celery
sudo systemctl restart utopiahire-beat

# 6. Verify
curl https://yourdomain.com/api/v1/health
```

## Support

- **Documentation**: `/docs/`
- **API Docs**: `https://yourdomain.com/api/docs`
- **Issues**: GitHub Issues
- **Email**: support@utopiahire.com
