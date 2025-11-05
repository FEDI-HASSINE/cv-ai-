# ⚡ Déploiement Express - 3 méthodes

## 🎯 Choisissez votre méthode

| Méthode | Temps | Coût | Difficulté |
|---------|-------|------|------------|
| [Docker Local](#docker-local) | 5 min | Gratuit | ⭐ Facile |
| [Heroku](#heroku) | 10 min | $7/mois | ⭐⭐ Moyen |
| [AWS EC2](#aws-ec2) | 20 min | $10/mois | ⭐⭐⭐ Avancé |

---

## 🐳 Docker Local

**Meilleur choix pour:** Développement, tests, démonstration

### Étape 1: Installer Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Vérifier
docker --version
docker-compose --version
```

### Étape 2: Cloner et configurer

```bash
git clone https://github.com/FEDI-HASSINE/cv-ai-.git
cd cv-ai-

# Créer le fichier .env
cp .env.example .env
nano .env

# Modifier:
# SECRET_KEY=votre-secret-key-256-bits-super-secure
# ALLOWED_ORIGINS=http://localhost:3000,https://votre-frontend.com
```

### Étape 3: Lancer avec Docker Compose

```bash
# Build et lancer
docker-compose up -d

# Vérifier les logs
docker-compose logs -f api

# Tester
curl http://localhost:8000/api/v1/health
# Response: {"status": "ok"}
```

### Étape 4: Tester l'analyse

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demopass123"}'

# Copier le access_token

# 2. Analyser un CV
curl -X POST http://localhost:8000/api/v1/resume/analyze \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -F "file=@cv.pdf"
```

### Arrêter

```bash
docker-compose down
```

✅ **Votre API est accessible sur:** `http://localhost:8000`

---

## 🟣 Heroku

**Meilleur choix pour:** Production rapide, pas d'administration serveur

### Étape 1: Créer un compte Heroku

1. Aller sur https://heroku.com
2. S'inscrire (gratuit)
3. Installer Heroku CLI:

```bash
curl https://cli-assets.heroku.com/install.sh | sh
heroku login
```

### Étape 2: Préparer le projet

```bash
git clone https://github.com/FEDI-HASSINE/cv-ai-.git
cd cv-ai-

# Créer Procfile
echo "web: uvicorn src.api.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Créer runtime.txt
echo "python-3.12.0" > runtime.txt

# Commit
git add Procfile runtime.txt
git commit -m "Add Heroku config"
```

### Étape 3: Créer l'application

```bash
heroku create cv-analyzer-api-demo

# Configurer les variables d'environnement
heroku config:set SECRET_KEY=votre-secret-key-secure
heroku config:set ALLOWED_ORIGINS=https://votre-frontend.com
```

### Étape 4: Déployer

```bash
git push heroku main

# Ouvrir l'application
heroku open

# Voir les logs
heroku logs --tail
```

✅ **Votre API est accessible sur:** `https://cv-analyzer-api-demo.herokuapp.com`

### Commandes utiles

```bash
# Voir les logs en temps réel
heroku logs --tail

# Redémarrer
heroku restart

# Ouvrir le dashboard
heroku open

# Variables d'environnement
heroku config

# Scaler (augmenter les ressources)
heroku ps:scale web=1
```

---

## ☁️ AWS EC2

**Meilleur choix pour:** Production avec contrôle total, scalabilité

### Étape 1: Créer une instance EC2

1. Connexion à AWS Console
2. EC2 → Launch Instance
3. Configuration:
   - **Nom:** cv-analyzer-api
   - **AMI:** Ubuntu 22.04 LTS
   - **Type:** t2.micro (gratuit tier eligible)
   - **Key pair:** Créer ou sélectionner
   - **Security Group:** Créer avec règles:
     * SSH (22) - Votre IP
     * HTTP (80) - Anywhere
     * HTTPS (443) - Anywhere
     * Custom TCP (8000) - Anywhere (temporaire)

4. Launch Instance
5. Note l'adresse IP publique

### Étape 2: Se connecter

```bash
# Télécharger la clé .pem
chmod 400 votre-cle.pem

# Se connecter
ssh -i votre-cle.pem ubuntu@VOTRE_IP
```

### Étape 3: Installer les dépendances

```bash
# Mettre à jour
sudo apt update && sudo apt upgrade -y

# Installer Python 3.12
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install -y python3.12 python3.12-venv python3.12-dev git nginx

# Installer Docker (optionnel mais recommandé)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker
```

### Étape 4: Déployer l'application

#### Option A: Avec Docker (Recommandé)

```bash
# Cloner
git clone https://github.com/FEDI-HASSINE/cv-ai-.git
cd cv-ai-

# Configurer
cp .env.example .env
nano .env
# Modifier SECRET_KEY et ALLOWED_ORIGINS

# Build et lancer
docker-compose up -d

# Vérifier
docker-compose logs -f api
curl http://localhost:8000/api/v1/health
```

#### Option B: Sans Docker

```bash
# Cloner
git clone https://github.com/FEDI-HASSINE/cv-ai-.git
cd cv-ai-

# Créer venv minimal
python3.12 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install --no-cache-dir -r requirements.minimal.txt

# Configurer
cp .env.example .env
nano .env

# Tester
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Étape 5: Créer un service systemd

```bash
sudo nano /etc/systemd/system/cv-api.service
```

```ini
[Unit]
Description=CV Analyzer API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cv-ai-
Environment="PATH=/home/ubuntu/cv-ai-/venv/bin"
ExecStart=/home/ubuntu/cv-ai-/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer
sudo systemctl daemon-reload
sudo systemctl enable cv-api
sudo systemctl start cv-api

# Vérifier
sudo systemctl status cv-api
curl http://localhost:8000/api/v1/health
```

### Étape 6: Configurer Nginx

```bash
sudo nano /etc/nginx/sites-available/cv-api
```

```nginx
server {
    listen 80;
    server_name VOTRE_IP;  # ou api.votre-domaine.com

    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activer
sudo ln -s /etc/nginx/sites-available/cv-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Étape 7: Installer HTTPS (Let's Encrypt)

```bash
# Installer Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtenir le certificat (remplacer par votre domaine)
sudo certbot --nginx -d api.votre-domaine.com

# Renouvellement automatique
sudo systemctl enable certbot.timer
```

✅ **Votre API est accessible sur:** `https://api.votre-domaine.com`

### Commandes utiles EC2

```bash
# Voir les logs
sudo journalctl -u cv-api -f

# Redémarrer le service
sudo systemctl restart cv-api

# Arrêter le service
sudo systemctl stop cv-api

# Mettre à jour le code
cd ~/cv-ai-
git pull
sudo systemctl restart cv-api

# Vérifier l'utilisation des ressources
htop
df -h
free -h
```

---

## 📊 Comparaison des méthodes

| Critère | Docker Local | Heroku | AWS EC2 |
|---------|--------------|--------|---------|
| **Temps de setup** | 5 min | 10 min | 20 min |
| **Coût mensuel** | Gratuit | $7 | $10 |
| **Maintenance** | Facile | Aucune | Moyenne |
| **Scalabilité** | Limitée | Automatique | Manuelle |
| **HTTPS** | Non | Oui | Oui (Certbot) |
| **Domaine custom** | Non | Oui | Oui |
| **Accès SSH** | N/A | Non | Oui |
| **Contrôle total** | Oui | Non | Oui |

---

## 🧪 Tester votre déploiement

### Test 1: Health Check

```bash
curl https://votre-api.com/api/v1/health
# Response attendue: {"status": "ok"}
```

### Test 2: Login

```bash
curl -X POST https://votre-api.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demopass123"}'

# Response attendue: {"access_token": "eyJ...", "token_type": "bearer"}
```

### Test 3: Analyse complète

```bash
# Remplacer TOKEN par le token obtenu
curl -X POST https://votre-api.com/api/v1/resume/analyze \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@cv.pdf"

# Response attendue: JSON avec scores et compétences
```

---

## 🔧 Dépannage

### Erreur: "Connection refused"

```bash
# Vérifier que le service tourne
# Docker:
docker-compose ps

# Systemd:
sudo systemctl status cv-api

# Vérifier les ports
netstat -tulpn | grep 8000
```

### Erreur: "502 Bad Gateway" (Nginx)

```bash
# Vérifier les logs Nginx
sudo tail -f /var/log/nginx/error.log

# Vérifier que l'API répond
curl http://localhost:8000/api/v1/health
```

### Erreur: "Module not found"

```bash
# Réinstaller les dépendances
source venv/bin/activate
pip install --no-cache-dir -r requirements.minimal.txt
```

### Erreur: "Out of memory"

```bash
# Vérifier la mémoire
free -h

# Augmenter le swap (EC2)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📝 Prochaines étapes

1. ✅ API déployée et accessible
2. 📧 Envoyer l'URL à l'équipe frontend
3. 📖 Partager la documentation: `docs/FRONTEND_INTEGRATION.md`
4. 🔐 Configurer les credentials de production
5. 📊 Mettre en place le monitoring (Sentry, Prometheus)
6. 🔄 Configurer le CI/CD (GitHub Actions)

---

## 🎉 Félicitations!

Votre API est maintenant déployée et prête à être utilisée par l'équipe frontend!

**Documentation à partager avec l'équipe frontend:**
- `docs/FRONTEND_INTEGRATION.md` - Guide d'intégration complet
- URL de l'API
- Credentials (email/password)
- Exemples de code pour React/Angular/Vue

**Support:** Pour toute question technique sur l'API, contacter l'équipe backend.
