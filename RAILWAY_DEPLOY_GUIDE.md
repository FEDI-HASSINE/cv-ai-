# 🚀 Guide de Déploiement Railway - Étape par Étape

## ✅ Prérequis (Déjà fait!)

- ✅ Code sur GitHub: `https://github.com/FEDI-HASSINE/cv-ai-`
- ✅ Dockerfile optimisé (178MB)
- ✅ Configuration validée
- ✅ Tests passés (11/11)

---

## 📋 Méthode 1: Déploiement via Interface Web (RECOMMANDÉ)

### Étape 1: Créer un compte Railway

1. Aller sur: **https://railway.app**
2. Cliquer sur **"Start a New Project"**
3. Choisir **"Login with GitHub"**
4. Autoriser Railway à accéder à vos repositories

### Étape 2: Créer un nouveau projet

1. Une fois connecté, cliquer sur **"New Project"**
2. Choisir **"Deploy from GitHub repo"**
3. Sélectionner le repository: **`FEDI-HASSINE/cv-ai-`**
4. Railway va automatiquement détecter le Dockerfile!

### Étape 3: Configurer les variables d'environnement

Dans le dashboard Railway, aller dans **"Variables"** et ajouter:

```bash
# Variables obligatoires
SECRET_KEY=<générer-une-clé-sécurisée>
JWT_SECRET=<générer-une-clé-jwt>
ALLOWED_ORIGINS=*
LOG_LEVEL=info
DEBUG=False
APP_ENV=production

# Variables optionnelles (pour fonctionnalités avancées)
GITHUB_TOKEN=<votre-token-github>
OPENAI_API_KEY=<votre-clé-openai>
```

**Pour générer les clés sécurisées:**
```bash
# Dans votre terminal local:
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"
```

### Étape 4: Modifier le Dockerfile pour Railway

Railway utilise une variable `$PORT` dynamique. Le Dockerfile est déjà configuré, mais vérifions:

```dockerfile
# Le CMD doit utiliser $PORT au lieu de 8000 en dur
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
```

### Étape 5: Déployer!

1. Railway va automatiquement:
   - Cloner votre repo
   - Construire l'image Docker
   - Déployer le conteneur
   - Générer une URL publique

2. Attendre 2-3 minutes pendant le build

3. Une fois terminé, vous verrez:
   ```
   ✅ Deployment successful
   🌐 Your app is live at: https://cv-ai-production.up.railway.app
   ```

### Étape 6: Tester l'API déployée

```bash
# Test de santé
curl https://votre-url.railway.app/api/v1/health

# Documentation
https://votre-url.railway.app/api/docs

# Authentification
curl -X POST https://votre-url.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demopass123"}'
```

---

## 📋 Méthode 2: Déploiement via Railway CLI (Alternative)

### Installation de Railway CLI

```bash
# Linux/Mac
curl -fsSL https://railway.app/install.sh | sh

# Vérifier l'installation
railway --version
```

### Connexion et déploiement

```bash
# Se connecter
railway login

# Créer un nouveau projet
railway init

# Lier au projet (si déjà créé)
railway link

# Ajouter les variables d'environnement
railway variables set SECRET_KEY="votre-secret-key"
railway variables set JWT_SECRET="votre-jwt-secret"
railway variables set ALLOWED_ORIGINS="*"
railway variables set DEBUG="False"

# Déployer
railway up

# Voir les logs
railway logs
```

---

## 🔧 Configuration Avancée

### Domaine personnalisé

1. Dans Railway dashboard → Settings → Domains
2. Ajouter votre domaine: `api.votre-domaine.com`
3. Configurer les DNS selon les instructions Railway

### Auto-déploiement

Railway déploie automatiquement à chaque `git push` sur la branche `main`.

Pour désactiver:
```bash
railway settings --auto-deploy=false
```

### Scaling

Railway ajuste automatiquement les ressources. Pour forcer:
```bash
railway scale --replicas=2
```

---

## 🎯 Après le Déploiement

### Partager l'API avec l'équipe

Une fois déployé, partagez:

```
📡 URL de l'API: https://votre-app.railway.app

📚 Documentation: https://votre-app.railway.app/api/docs

🔑 Authentification:
   Endpoint: POST /api/v1/auth/login
   Body: {"email":"demo@example.com","password":"demopass123"}
   
📝 Exemple d'utilisation:

const API_URL = "https://votre-app.railway.app"
const token = "obtenu-via-login"

fetch(`${API_URL}/api/v1/resume/analyze`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
})
```

### Frontend React - Modifier l'URL de l'API

Dans votre code React:
```javascript
// Avant (local):
const API_URL = "http://localhost:4000"

// Après (production):
const API_URL = "https://votre-app.railway.app"
```

---

## 🐛 Résolution de Problèmes

### Le build échoue

```bash
# Voir les logs de build
railway logs --deployment

# Vérifier les variables d'environnement
railway variables
```

### L'API ne répond pas

1. Vérifier le health check: `/api/v1/health`
2. Voir les logs: `railway logs`
3. Vérifier les variables d'environnement
4. S'assurer que le port utilise `$PORT`

### Timeout lors du démarrage

Augmenter le timeout dans les settings Railway:
- Healthcheck timeout: 300s
- Start timeout: 180s

---

## 💰 Coûts

### Plan Gratuit (Trial)
- $5 de crédit gratuit/mois
- Suffisant pour ~500 heures d'exécution
- Pas de carte de crédit requise

### Plan Hobby ($5/mois)
- $5 de crédit inclus
- Puis pay-as-you-go
- ~$0.01/heure d'exécution

### Estimation pour votre API
- **Utilisation légère** (quelques requêtes/jour): Gratuit
- **Utilisation moyenne** (100+ requêtes/jour): ~$2-3/mois
- **Utilisation intensive**: ~$10-20/mois

---

## ✅ Checklist de Déploiement

Avant de déployer:

- [ ] Code poussé sur GitHub
- [ ] Variables d'environnement préparées
- [ ] Dockerfile testé localement
- [ ] Health check fonctionne
- [ ] Documentation à jour

Après le déploiement:

- [ ] Health check répond 200
- [ ] Documentation accessible (/api/docs)
- [ ] Authentification fonctionne
- [ ] Test d'upload de CV réussi
- [ ] URL partagée avec l'équipe

---

## 🆘 Support

**Railway:**
- Documentation: https://docs.railway.app
- Discord: https://discord.gg/railway
- Support: support@railway.app

**Votre API:**
- Repository: https://github.com/FEDI-HASSINE/cv-ai-
- Documentation locale: Voir DOCKER_DEPLOY.md

---

## 🎉 Prochaines Étapes

Une fois l'API déployée:

1. ✅ Tester tous les endpoints en production
2. ✅ Configurer le monitoring (Railway inclut)
3. ✅ Mettre à jour le frontend React avec la nouvelle URL
4. ✅ Partager la documentation API avec l'équipe
5. ✅ Configurer les alertes (optionnel)
6. ✅ Ajouter un domaine personnalisé (optionnel)

---

**🚀 Votre API sera accessible 24/7 depuis n'importe où dans le monde!**
