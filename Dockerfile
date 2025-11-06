# 🐳 Dockerfile optimisé pour l'API d'analyse de CV
# Image finale: ~250MB (vs 3GB venv local)

FROM python:3.12-slim

# Métadonnées
LABEL maintainer="votre-email@example.com"
LABEL description="API d'analyse de CV avec FastAPI et NLP"
LABEL version="1.0.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Créer un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 appuser

# Définir le répertoire de travail
WORKDIR /app

# Copier uniquement les requirements d'abord (cache Docker)
COPY requirements.minimal.txt .

# Installer les dépendances système nécessaires
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        && \
    pip install --no-cache-dir -r requirements.minimal.txt && \
    apt-get purge -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copier le code source
COPY --chown=appuser:appuser src/ ./src/

# Créer un fichier .env par défaut (sera remplacé par volume en prod)
RUN echo "SECRET_KEY=docker-default-secret-key-change-in-production" > .env && \
    echo "JWT_SECRET=docker-jwt-secret-change-in-production" >> .env && \
    echo "ALLOWED_ORIGINS=http://localhost:3000" >> .env && \
    echo "LOG_LEVEL=info" >> .env && \
    echo "DEBUG=False" >> .env && \
    echo "APP_ENV=docker" >> .env

# Créer les répertoires nécessaires
RUN mkdir -p logs reports temp && \
    chown -R appuser:appuser /app

# Passer à l'utilisateur non-root
USER appuser

# Exposer le port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Commande de démarrage (supporte Railway $PORT)
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
