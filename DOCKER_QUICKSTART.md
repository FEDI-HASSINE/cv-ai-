# 🚀 Démarrage Rapide - Docker

## En 30 secondes

```bash
# 1. Construire l'image
docker build -t cv-api:latest .

# 2. Démarrer le conteneur
docker-compose up -d api

# 3. Tester
curl http://localhost:8000/api/v1/health
```

Voir documentation complète: **[DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)**

---

## Test Automatique

```bash
./scripts/test_docker.sh
```

---

## Endpoints

| Endpoint | URL |
|----------|-----|
| **Documentation** | http://localhost:8000/api/docs |
| **Health Check** | http://localhost:8000/api/v1/health |
| **Login** | POST http://localhost:8000/api/v1/auth/login |

**Identifiants de test:**
- Email: `demo@example.com`
- Password: `demopass123`

---

## Image Docker

- **Taille:** 178 MB ✅
- **Base:** python:3.12-slim
- **Status:** Validé et testé
- **Mémoire:** ~130 MB RAM
- **CPU:** <1%

---

## Commandes Utiles

```bash
# Voir les logs
docker logs cv-analyzer-api -f

# Arrêter
docker-compose down

# Redémarrer
docker-compose restart api

# Stats
docker stats cv-analyzer-api
```

---

## Déploiement Production

Voir le guide complet: **[DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)**

Options recommandées:
- 🚂 **Railway.app** - Auto-deploy depuis GitHub
- 🎨 **Render.com** - Free tier disponible
- ☁️ **AWS ECS** - Production enterprise
