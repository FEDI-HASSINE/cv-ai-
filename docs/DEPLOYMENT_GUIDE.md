# 🚀 Guide de Déploiement - API d'Analyse de CV

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Options de déploiement](#options-de-déploiement)
3. [Configuration pour l'équipe frontend](#configuration-pour-léquipe-frontend)
4. [Exemples d'intégration](#exemples-dintégration)
5. [Sécurité et production](#sécurité-et-production)

---

## 🎯 Vue d'ensemble

### Architecture Client-Serveur

```
┌─────────────────────┐
│   ÉQUIPE FRONTEND   │
│  (React/Angular/    │
│   Vue/Vanilla JS)   │
│                     │
│  Ils développent:   │
│  • Interface UI     │
│  • Upload CV        │
│  • Affichage résult │
└──────────┬──────────┘
           │
           │ HTTP POST /api/v1/resume/analyze
           │ (multipart/form-data)
           │
           ▼
┌──────────────────────┐
│   SERVEUR BACKEND    │
│   (FastAPI + AI)     │
│                      │
│  Vous déployez:      │
│  • Parsing CV        │
│  • Analyse AI/NLP    │
│  • Calcul scores     │
│  • API REST          │
└──────────────────────┘
```

### ✅ Principe clé

**L'équipe frontend n'a PAS besoin:**
- ❌ Du code Python
- ❌ De venv ou pip
- ❌ De PyPDF2, python-docx
- ❌ De ce repository Git
- ❌ D'installer FastAPI

**Ils ont seulement besoin:**
- ✅ URL de l'API: `http://votre-serveur:8000`
- ✅ Credentials (email/password) pour authentification
- ✅ Documentation API (endpoints, format JSON)

---

## 🚀 Options de déploiement

### Option 1: Docker (Recommandé) 🐳

**Avantages:** Isolation complète, pas de problèmes de dépendances, facile à déployer

#### Étape 1: Créer le Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les requirements
COPY requirements.minimal.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.minimal.txt

# Copier le code source
COPY src/ ./src/
COPY .env .env

# Exposer le port
EXPOSE 8000

# Lancer l'application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Étape 2: Build et lancer

```bash
# Build l'image
docker build -t cv-analyzer-api .

# Lancer le conteneur
docker run -d -p 8000:8000 --name cv-api cv-analyzer-api

# Vérifier les logs
docker logs -f cv-api

# Tester
curl http://localhost:8000/api/v1/health
```

#### Étape 3: Docker Compose (avec persistance)

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./reports:/app/reports
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_ORIGINS=https://votre-frontend.com
    restart: unless-stopped
```

```bash
# Lancer avec docker-compose
docker-compose up -d

# Arrêter
docker-compose down
```

---

### Option 2: AWS EC2 ☁️

**Avantages:** Contrôle total, scalabilité, pas cher (~$10/mois)

#### Étape 1: Créer une instance EC2

1. Connexion à AWS Console
2. EC2 → Launch Instance
3. Choisir: **Ubuntu 22.04 LTS**
4. Type: **t2.micro** (gratuit tier eligible)
5. Security Group: Ouvrir port **8000**

#### Étape 2: Se connecter et installer

```bash
# Se connecter via SSH
ssh -i votre-cle.pem ubuntu@VOTRE_IP

# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer Python et dépendances
sudo apt install -y python3.12 python3.12-venv git

# Cloner le repository
git clone https://github.com/FEDI-HASSINE/cv-ai-.git
cd cv-ai-

# Créer venv minimal
python3.12 -m venv venv
source venv/bin/activate

# Installer dépendances minimales
pip install --no-cache-dir -r requirements.minimal.txt

# Créer fichier .env
nano .env
# Ajouter:
# SECRET_KEY=votre-secret-key-tres-secure
# ALLOWED_ORIGINS=https://votre-frontend.com

# Tester en développement
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

#### Étape 3: Configuration avec systemd (service permanent)

```bash
# Créer le service
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
ExecStart=/home/ubuntu/cv-ai-/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer le service
sudo systemctl daemon-reload
sudo systemctl enable cv-api
sudo systemctl start cv-api

# Vérifier le statut
sudo systemctl status cv-api

# Voir les logs
sudo journalctl -u cv-api -f
```

#### Étape 4: Configurer Nginx (reverse proxy + HTTPS)

```bash
# Installer Nginx et Certbot
sudo apt install -y nginx certbot python3-certbot-nginx

# Configurer Nginx
sudo nano /etc/nginx/sites-available/cv-api
```

```nginx
server {
    listen 80;
    server_name api.votre-domaine.com;

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
# Activer le site
sudo ln -s /etc/nginx/sites-available/cv-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Installer le certificat SSL (HTTPS)
sudo certbot --nginx -d api.votre-domaine.com

# Votre API est maintenant accessible via:
# https://api.votre-domaine.com
```

---

### Option 3: Heroku (Le plus simple) 🟣

**Avantages:** Zero configuration, déploiement en 5 minutes

#### Étape 1: Préparer les fichiers

```bash
# Créer Procfile
echo "web: uvicorn src.api.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Créer runtime.txt
echo "python-3.12.0" > runtime.txt
```

#### Étape 2: Déployer

```bash
# Installer Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Créer l'application
heroku create cv-analyzer-api

# Configurer les variables d'environnement
heroku config:set SECRET_KEY=votre-secret-key-secure

# Déployer
git push heroku main

# Ouvrir l'application
heroku open

# Votre API est accessible à:
# https://cv-analyzer-api.herokuapp.com
```

---

### Option 4: DigitalOcean App Platform 🌊

**Avantages:** Similaire à Heroku, $5/mois, simple

1. Créer un compte DigitalOcean
2. Apps → Create App
3. Connecter votre GitHub repository
4. Choisir: **Python**
5. Run command: `uvicorn src.api.main:app --host 0.0.0.0 --port 8080`
6. Déployer automatiquement!

---

## 🔌 Configuration pour l'équipe frontend

### Informations à fournir

Une fois déployé, donnez ces informations à l'équipe frontend:

```javascript
// Configuration API
const API_CONFIG = {
  BASE_URL: "https://api.votre-domaine.com",  // Votre URL de production
  AUTH_EMAIL: "demo@example.com",              // Credentials
  AUTH_PASSWORD: "demopass123",
  ENDPOINTS: {
    LOGIN: "/api/v1/auth/login",
    ANALYZE: "/api/v1/resume/analyze"
  }
};
```

### Documentation API simple

```markdown
# API d'Analyse de CV - Documentation

## 1. Authentification

**POST /api/v1/auth/login**

Request:
```json
{
  "email": "demo@example.com",
  "password": "demopass123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "token_type": "bearer"
}
```

## 2. Analyser un CV

**POST /api/v1/resume/analyze**

Headers:
- `Authorization: Bearer {access_token}`

Body (multipart/form-data):
- `file`: Le fichier CV (PDF ou DOCX)

Response:
```json
{
  "overall_score": 96,
  "ats_score": 99,
  "technical_skills": ["Python", "React", "Docker"],
  "soft_skills": ["Leadership", "Communication"],
  "experience_years": 5.0,
  "strengths": ["Strong technical background", "..."],
  "weaknesses": ["Limited project management experience"],
  "suggestions": ["Add more quantifiable achievements"]
}
```
```

---

## 💻 Exemples d'intégration

### React (avec hooks)

```javascript
// src/services/cvAnalyzer.js
const API_URL = "https://api.votre-domaine.com";

class CVAnalyzerService {
  constructor() {
    this.token = null;
  }

  async login() {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'demo@example.com',
        password: 'demopass123'
      })
    });

    const data = await response.json();
    this.token = data.access_token;
    return this.token;
  }

  async analyzeResume(file) {
    if (!this.token) await this.login();

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/api/v1/resume/analyze`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }
}

export default new CVAnalyzerService();
```

```javascript
// src/components/CVUploader.jsx
import React, { useState } from 'react';
import cvService from '../services/cvAnalyzer';

const CVUploader = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const analysis = await cvService.analyzeResume(file);
      setResult(analysis);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cv-uploader">
      <input 
        type="file" 
        accept=".pdf,.docx"
        onChange={handleFileUpload}
        disabled={loading}
      />

      {loading && <p>Analyse en cours...</p>}
      {error && <p className="error">{error}</p>}

      {result && (
        <div className="results">
          <h2>Résultats de l'analyse</h2>
          <div className="scores">
            <div className="score">
              <span>Score Global</span>
              <strong>{result.overall_score}/100</strong>
            </div>
            <div className="score">
              <span>Score ATS</span>
              <strong>{result.ats_score}/100</strong>
            </div>
          </div>

          <div className="skills">
            <h3>Compétences Techniques</h3>
            <ul>
              {result.technical_skills.map((skill, idx) => (
                <li key={idx}>{skill}</li>
              ))}
            </ul>
          </div>

          <div className="suggestions">
            <h3>Suggestions d'amélioration</h3>
            <ul>
              {result.suggestions.map((suggestion, idx) => (
                <li key={idx}>{suggestion}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default CVUploader;
```

### Angular

```typescript
// src/app/services/cv-analyzer.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, from } from 'rxjs';
import { switchMap } from 'rxjs/operators';

interface AnalysisResult {
  overall_score: number;
  ats_score: number;
  technical_skills: string[];
  soft_skills: string[];
  experience_years: number;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
}

@Injectable({
  providedIn: 'root'
})
export class CvAnalyzerService {
  private apiUrl = 'https://api.votre-domaine.com';
  private token: string | null = null;

  constructor(private http: HttpClient) {}

  private async login(): Promise<string> {
    const response = await fetch(`${this.apiUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'demo@example.com',
        password: 'demopass123'
      })
    });

    const data = await response.json();
    this.token = data.access_token;
    return this.token;
  }

  analyzeResume(file: File): Observable<AnalysisResult> {
    return from(this.login()).pipe(
      switchMap(token => {
        const formData = new FormData();
        formData.append('file', file);

        const headers = new HttpHeaders({
          'Authorization': `Bearer ${token}`
        });

        return this.http.post<AnalysisResult>(
          `${this.apiUrl}/api/v1/resume/analyze`,
          formData,
          { headers }
        );
      })
    );
  }
}
```

### Vue.js

```javascript
// src/services/cvAnalyzer.js
import axios from 'axios';

const API_URL = 'https://api.votre-domaine.com';

class CVAnalyzerService {
  constructor() {
    this.client = axios.create({
      baseURL: API_URL
    });
    this.token = null;
  }

  async login() {
    const response = await this.client.post('/api/v1/auth/login', {
      email: 'demo@example.com',
      password: 'demopass123'
    });

    this.token = response.data.access_token;
    this.client.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
    return this.token;
  }

  async analyzeResume(file) {
    if (!this.token) await this.login();

    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/api/v1/resume/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    return response.data;
  }
}

export default new CVAnalyzerService();
```

```vue
<!-- src/components/CVUploader.vue -->
<template>
  <div class="cv-uploader">
    <input 
      type="file" 
      @change="handleFileUpload"
      accept=".pdf,.docx"
      :disabled="loading"
    />

    <div v-if="loading" class="loading">
      Analyse en cours...
    </div>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="result" class="results">
      <h2>Résultats de l'analyse</h2>
      
      <div class="scores">
        <div class="score-card">
          <span>Score Global</span>
          <strong>{{ result.overall_score }}/100</strong>
        </div>
        <div class="score-card">
          <span>Score ATS</span>
          <strong>{{ result.ats_score }}/100</strong>
        </div>
      </div>

      <div class="skills">
        <h3>Compétences Techniques</h3>
        <ul>
          <li v-for="(skill, idx) in result.technical_skills" :key="idx">
            {{ skill }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import cvService from '@/services/cvAnalyzer';

export default {
  name: 'CVUploader',
  data() {
    return {
      loading: false,
      result: null,
      error: null
    };
  },
  methods: {
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      this.loading = true;
      this.error = null;
      this.result = null;

      try {
        this.result = await cvService.analyzeResume(file);
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

### Vanilla JavaScript (pas de framework)

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Analyseur de CV</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
    .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; }
    .results { margin-top: 20px; }
    .score { display: inline-block; margin: 10px; padding: 20px; background: #f0f0f0; }
  </style>
</head>
<body>
  <h1>Analyseur de CV</h1>
  
  <div class="upload-area">
    <input type="file" id="cvFile" accept=".pdf,.docx">
    <p>Déposez votre CV ici</p>
  </div>

  <div id="loading" style="display: none;">Analyse en cours...</div>
  <div id="error" style="color: red; display: none;"></div>
  <div id="results" style="display: none;"></div>

  <script>
    const API_URL = 'https://api.votre-domaine.com';
    let token = null;

    async function login() {
      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'demo@example.com',
          password: 'demopass123'
        })
      });

      const data = await response.json();
      token = data.access_token;
      return token;
    }

    async function analyzeCV(file) {
      if (!token) await login();

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/api/v1/resume/analyze`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      return await response.json();
    }

    document.getElementById('cvFile').addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const loading = document.getElementById('loading');
      const error = document.getElementById('error');
      const results = document.getElementById('results');

      loading.style.display = 'block';
      error.style.display = 'none';
      results.style.display = 'none';

      try {
        const analysis = await analyzeCV(file);

        results.innerHTML = `
          <h2>Résultats de l'analyse</h2>
          <div class="score">
            <strong>Score Global</strong><br>
            ${analysis.overall_score}/100
          </div>
          <div class="score">
            <strong>Score ATS</strong><br>
            ${analysis.ats_score}/100
          </div>
          <h3>Compétences Techniques</h3>
          <ul>
            ${analysis.technical_skills.map(s => `<li>${s}</li>`).join('')}
          </ul>
          <h3>Suggestions</h3>
          <ul>
            ${analysis.suggestions.map(s => `<li>${s}</li>`).join('')}
          </ul>
        `;

        results.style.display = 'block';
      } catch (err) {
        error.textContent = `Erreur: ${err.message}`;
        error.style.display = 'block';
      } finally {
        loading.style.display = 'none';
      }
    });
  </script>
</body>
</html>
```

---

## 🔒 Sécurité et production

### Checklist de sécurité

- [ ] **Variables d'environnement**
  ```bash
  # .env (jamais commiter!)
  SECRET_KEY=votre-cle-super-secrete-256-bits
  ALLOWED_ORIGINS=https://votre-frontend.com
  DATABASE_URL=postgresql://user:pass@host:5432/db
  ```

- [ ] **HTTPS uniquement** (Certbot/Let's Encrypt)
  ```nginx
  # Rediriger HTTP → HTTPS
  server {
      listen 80;
      return 301 https://$host$request_uri;
  }
  ```

- [ ] **Rate limiting** (limite les abus)
  ```python
  # Dans src/api/middleware.py
  from slowapi import Limiter
  from slowapi.util import get_remote_address

  limiter = Limiter(key_func=get_remote_address)

  @app.post("/api/v1/resume/analyze")
  @limiter.limit("10/minute")  # Max 10 requêtes/minute
  async def analyze_resume(...):
      ...
  ```

- [ ] **CORS strict**
  ```python
  # Dans src/api/main.py
  origins = [
      "https://votre-frontend.com",  # Production uniquement
      # Pas de "*" en production!
  ]
  ```

- [ ] **Validation stricte des fichiers**
  ```python
  # Vérifier:
  # - Taille max (10 MB)
  # - Extensions autorisées (.pdf, .docx)
  # - Content-Type valide
  # - Scanner antivirus (optionnel mais recommandé)
  ```

- [ ] **Logs et monitoring**
  ```python
  # Intégrer:
  # - Sentry (errors tracking)
  # - Prometheus (métriques)
  # - CloudWatch/Datadog (monitoring)
  ```

### Configuration de production recommandée

```python
# src/api/main.py (production)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import sentry_sdk

# Initialiser Sentry pour le tracking d'erreurs
sentry_sdk.init(
    dsn="votre-sentry-dsn",
    traces_sample_rate=1.0
)

app = FastAPI(
    title="CV Analyzer API",
    version="1.0.0",
    docs_url=None,  # Désactiver /docs en production
    redoc_url=None   # Désactiver /redoc en production
)

# Middleware de sécurité
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.votre-domaine.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://votre-frontend.com"],  # Pas de wildcard!
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## 📊 Monitoring et maintenance

### Vérifier la santé de l'API

```bash
# Health check
curl https://api.votre-domaine.com/api/v1/health

# Response attendue:
# {"status": "ok", "version": "1.0.0"}
```

### Logs

```bash
# Docker
docker logs -f cv-api

# Systemd (EC2)
sudo journalctl -u cv-api -f

# Heroku
heroku logs --tail
```

### Métriques à surveiller

- **Temps de réponse** (devrait être < 5 secondes)
- **Taux d'erreur** (devrait être < 1%)
- **Utilisation CPU/RAM**
- **Nombre de requêtes par minute**

---

## 💰 Coûts estimés

| Option | Coût mensuel | Avantages |
|--------|--------------|-----------|
| Heroku Hobby | $7/mois | Simple, zero config |
| DigitalOcean | $5/mois | Bon rapport qualité/prix |
| AWS EC2 t2.micro | $10/mois | Scalable, contrôle total |
| Docker + VPS | $5-10/mois | Flexible, portable |

---

## 🎯 Checklist finale de déploiement

- [ ] Choisir une option de déploiement
- [ ] Configurer les variables d'environnement (SECRET_KEY, etc.)
- [ ] Déployer l'API
- [ ] Configurer HTTPS (certificat SSL)
- [ ] Tester tous les endpoints
- [ ] Configurer CORS pour le domaine frontend
- [ ] Documenter l'API pour l'équipe frontend
- [ ] Fournir: URL + Credentials + Exemples de code
- [ ] Mettre en place monitoring/alertes
- [ ] Créer une stratégie de backup

---

## 📞 Support

Une fois déployé, l'équipe frontend peut tester avec:

```bash
# 1. Test d'authentification
curl -X POST https://api.votre-domaine.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demopass123"}'

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 2. Test d'analyse (remplacer TOKEN)
curl -X POST https://api.votre-domaine.com/api/v1/resume/analyze \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@cv.pdf"

# Response: {...analyse complète...}
```

---

**Vous êtes prêt! 🚀 L'équipe frontend peut maintenant intégrer l'API sans toucher au code backend.**
