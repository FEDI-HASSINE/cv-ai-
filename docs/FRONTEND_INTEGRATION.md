# 🎨 Guide d'intégration Frontend - API d'Analyse de CV

> **Pour l'équipe frontend uniquement** - Vous n'avez pas besoin du code backend!

---

## 🎯 Qu'est-ce que vous devez savoir?

### Vous avez juste besoin de:

1. ✅ **URL de l'API**: `https://api.votre-domaine.com`
2. ✅ **Credentials** pour l'authentification
3. ✅ **2 endpoints** à appeler

### Vous n'avez PAS besoin de:

- ❌ Installer Python
- ❌ Cloner le repository backend
- ❌ Gérer venv, pip, ou dependencies Python
- ❌ Comprendre FastAPI ou le code AI
- ❌ Lire la documentation backend

**Tout se fait via HTTP!** 🌐

---

## 🚀 Quick Start (5 minutes)

### Étape 1: Configuration

```javascript
// config.js
export const API_CONFIG = {
  BASE_URL: "https://api.votre-domaine.com",  // URL fournie par l'équipe backend
  AUTH: {
    EMAIL: "demo@example.com",      // Credentials fournis
    PASSWORD: "demopass123"
  }
};
```

### Étape 2: Service d'authentification

```javascript
// services/auth.js
import { API_CONFIG } from './config';

export async function login() {
  const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: API_CONFIG.AUTH.EMAIL,
      password: API_CONFIG.AUTH.PASSWORD
    })
  });

  const data = await response.json();
  return data.access_token;  // Sauvegarder ce token!
}
```

### Étape 3: Analyser un CV

```javascript
// services/cvAnalyzer.js
import { API_CONFIG } from './config';
import { login } from './auth';

let token = null;

export async function analyzeCV(file) {
  // 1. Se connecter si pas de token
  if (!token) {
    token = await login();
  }

  // 2. Préparer le fichier
  const formData = new FormData();
  formData.append('file', file);

  // 3. Envoyer la requête
  const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/resume/analyze`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });

  // 4. Retourner les résultats
  return await response.json();
}
```

### Étape 4: Utiliser dans votre composant

```javascript
// App.js (React example)
import React, { useState } from 'react';
import { analyzeCV } from './services/cvAnalyzer';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    
    setLoading(true);
    try {
      const analysis = await analyzeCV(file);
      setResult(analysis);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleFileUpload} accept=".pdf,.docx" />
      
      {loading && <p>Analyse en cours...</p>}
      
      {result && (
        <div>
          <h2>Score: {result.overall_score}/100</h2>
          <p>Score ATS: {result.ats_score}/100</p>
          <ul>
            {result.technical_skills.map(skill => <li key={skill}>{skill}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
```

**C'est tout! Vous êtes prêt! 🎉**

---

## 📡 API Reference

### 1. Authentification

**Endpoint:** `POST /api/v1/auth/login`

**Request:**
```json
{
  "email": "demo@example.com",
  "password": "demopass123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Usage:**
```javascript
const token = response.access_token;
// Sauvegarder dans localStorage ou state
localStorage.setItem('token', token);
```

---

### 2. Analyse de CV

**Endpoint:** `POST /api/v1/resume/analyze`

**Headers:**
```
Authorization: Bearer {votre_token}
Content-Type: multipart/form-data
```

**Body:**
- `file`: Fichier CV (PDF ou DOCX, max 10MB)

**Response:**
```json
{
  "overall_score": 96,
  "ats_score": 99,
  "technical_skills": [
    "Python",
    "React",
    "Docker",
    "AWS",
    "...plus"
  ],
  "soft_skills": [
    "Leadership",
    "Communication",
    "Problem Solving"
  ],
  "experience_years": 5.0,
  "strengths": [
    "Strong technical background in full-stack development",
    "Excellent project management skills",
    "Clear communication style"
  ],
  "weaknesses": [
    "Limited experience with machine learning",
    "Could add more quantifiable achievements"
  ],
  "suggestions": [
    "Add metrics to achievements (e.g., 'Improved performance by 40%')",
    "Include certifications or training courses",
    "Add a professional summary at the top"
  ]
}
```

---

## 💻 Exemples complets par framework

### React (avec Axios)

```bash
npm install axios
```

```javascript
// services/api.js
import axios from 'axios';

const API = axios.create({
  baseURL: 'https://api.votre-domaine.com',
});

// Interceptor pour ajouter le token automatiquement
API.interceptors.request.use(async (config) => {
  let token = localStorage.getItem('token');
  
  if (!token) {
    // Login automatique
    const response = await axios.post(`${config.baseURL}/api/v1/auth/login`, {
      email: 'demo@example.com',
      password: 'demopass123'
    });
    token = response.data.access_token;
    localStorage.setItem('token', token);
  }
  
  config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const analyzeCV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await API.post('/api/v1/resume/analyze', formData);
  return response.data;
};
```

```javascript
// Component.jsx
import { analyzeCV } from './services/api';

function CVAnalyzer() {
  const [result, setResult] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    const analysis = await analyzeCV(file);
    setResult(analysis);
  };

  return (
    <>
      <input type="file" onChange={handleUpload} />
      {result && <Results data={result} />}
    </>
  );
}
```

---

### Angular

```typescript
// services/cv-analyzer.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, from } from 'rxjs';
import { switchMap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class CvAnalyzerService {
  private apiUrl = 'https://api.votre-domaine.com';
  private token: string | null = null;

  constructor(private http: HttpClient) {}

  private async getToken(): Promise<string> {
    if (this.token) return this.token;

    const response: any = await this.http.post(
      `${this.apiUrl}/api/v1/auth/login`,
      { email: 'demo@example.com', password: 'demopass123' }
    ).toPromise();

    this.token = response.access_token;
    return this.token;
  }

  analyzeResume(file: File): Observable<any> {
    return from(this.getToken()).pipe(
      switchMap(token => {
        const formData = new FormData();
        formData.append('file', file);

        return this.http.post(
          `${this.apiUrl}/api/v1/resume/analyze`,
          formData,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      })
    );
  }
}
```

```typescript
// component.ts
import { Component } from '@angular/core';
import { CvAnalyzerService } from './services/cv-analyzer.service';

@Component({
  selector: 'app-cv-uploader',
  template: `
    <input type="file" (change)="onFileChange($event)" />
    <div *ngIf="result">
      <h2>Score: {{ result.overall_score }}/100</h2>
    </div>
  `
})
export class CvUploaderComponent {
  result: any;

  constructor(private cvService: CvAnalyzerService) {}

  onFileChange(event: any) {
    const file = event.target.files[0];
    this.cvService.analyzeResume(file).subscribe(
      data => this.result = data
    );
  }
}
```

---

### Vue.js 3 (Composition API)

```javascript
// composables/useCVAnalyzer.js
import { ref } from 'vue';

export function useCVAnalyzer() {
  const API_URL = 'https://api.votre-domaine.com';
  const result = ref(null);
  const loading = ref(false);
  const error = ref(null);

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
    return data.access_token;
  }

  async function analyzeCV(file) {
    loading.value = true;
    error.value = null;

    try {
      const token = await login();
      
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/api/v1/resume/analyze`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      result.value = await response.json();
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  }

  return {
    result,
    loading,
    error,
    analyzeCV
  };
}
```

```vue
<!-- CVUploader.vue -->
<template>
  <div>
    <input type="file" @change="handleUpload" />
    <p v-if="loading">Analyse en cours...</p>
    <div v-if="result">
      <h2>Score: {{ result.overall_score }}/100</h2>
      <p>ATS: {{ result.ats_score }}/100</p>
    </div>
  </div>
</template>

<script setup>
import { useCVAnalyzer } from './composables/useCVAnalyzer';

const { result, loading, analyzeCV } = useCVAnalyzer();

const handleUpload = (event) => {
  const file = event.target.files[0];
  if (file) analyzeCV(file);
};
</script>
```

---

### Vanilla JavaScript (pas de framework)

```html
<!DOCTYPE html>
<html>
<head>
  <title>CV Analyzer</title>
</head>
<body>
  <input type="file" id="fileInput" accept=".pdf,.docx" />
  <div id="result"></div>

  <script>
    const API_URL = 'https://api.votre-domaine.com';
    let token = null;

    async function getToken() {
      if (token) return token;

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
      const authToken = await getToken();
      
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/api/v1/resume/analyze`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken}` },
        body: formData
      });

      return await response.json();
    }

    document.getElementById('fileInput').addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const result = await analyzeCV(file);
      
      document.getElementById('result').innerHTML = `
        <h2>Score: ${result.overall_score}/100</h2>
        <p>ATS: ${result.ats_score}/100</p>
        <h3>Compétences:</h3>
        <ul>${result.technical_skills.map(s => `<li>${s}</li>`).join('')}</ul>
      `;
    });
  </script>
</body>
</html>
```

---

## ⚠️ Gestion des erreurs

```javascript
async function analyzeCV(file) {
  try {
    const token = await getToken();
    
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/api/v1/resume/analyze`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });

    // Vérifier le statut
    if (!response.ok) {
      if (response.status === 401) {
        // Token expiré, réessayer
        token = null;
        return analyzeCV(file);  // Retry
      }
      
      if (response.status === 413) {
        throw new Error('Fichier trop volumineux (max 10MB)');
      }
      
      if (response.status === 415) {
        throw new Error('Format de fichier non supporté (.pdf ou .docx uniquement)');
      }
      
      throw new Error(`Erreur HTTP: ${response.status}`);
    }

    return await response.json();
    
  } catch (error) {
    console.error('Erreur lors de l\'analyse:', error);
    throw error;
  }
}
```

---

## 🔐 Sécurité

### ✅ Bonnes pratiques

```javascript
// 1. Ne jamais exposer les credentials dans le code frontend
// Les stocker dans des variables d'environnement

// .env
VITE_API_URL=https://api.votre-domaine.com
VITE_API_EMAIL=demo@example.com
VITE_API_PASSWORD=demopass123

// Utilisation
const API_URL = import.meta.env.VITE_API_URL;

// 2. Valider les fichiers côté client
function validateFile(file) {
  const maxSize = 10 * 1024 * 1024; // 10MB
  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
  
  if (file.size > maxSize) {
    throw new Error('Fichier trop volumineux (max 10MB)');
  }
  
  if (!allowedTypes.includes(file.type)) {
    throw new Error('Format non supporté (.pdf ou .docx uniquement)');
  }
  
  return true;
}

// 3. Gérer l'expiration du token
// Le token expire après 24h
// Stocker avec timestamp et renouveler si nécessaire
function saveToken(token) {
  localStorage.setItem('token', token);
  localStorage.setItem('token_timestamp', Date.now().toString());
}

function isTokenValid() {
  const timestamp = localStorage.getItem('token_timestamp');
  if (!timestamp) return false;
  
  const age = Date.now() - parseInt(timestamp);
  const maxAge = 24 * 60 * 60 * 1000; // 24 heures
  
  return age < maxAge;
}
```

---

## 🧪 Tester l'API (avant d'intégrer)

### Avec curl

```bash
# 1. Login
curl -X POST https://api.votre-domaine.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demopass123"}'

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 2. Analyser (remplacer TOKEN)
curl -X POST https://api.votre-domaine.com/api/v1/resume/analyze \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@mon-cv.pdf"
```

### Avec Postman

1. **Login**
   - Method: POST
   - URL: `https://api.votre-domaine.com/api/v1/auth/login`
   - Body → raw → JSON:
     ```json
     {
       "email": "demo@example.com",
       "password": "demopass123"
     }
     ```
   - Copier le `access_token` de la réponse

2. **Analyze**
   - Method: POST
   - URL: `https://api.votre-domaine.com/api/v1/resume/analyze`
   - Headers:
     - `Authorization`: `Bearer {votre_token}`
   - Body → form-data:
     - Key: `file` (type: File)
     - Value: Sélectionner un fichier PDF/DOCX

---

## 📞 Support

### Questions fréquentes

**Q: L'API ne répond pas?**
```javascript
// Vérifier le statut de l'API
fetch('https://api.votre-domaine.com/api/v1/health')
  .then(r => r.json())
  .then(console.log);
// Response attendue: {"status": "ok"}
```

**Q: Erreur 401 Unauthorized?**
- Le token a expiré (durée de vie: 24h)
- Refaire un login pour obtenir un nouveau token

**Q: Erreur CORS?**
- Contacter l'équipe backend pour ajouter votre domaine aux origines autorisées

**Q: L'analyse prend trop de temps?**
- Temps normal: 2-5 secondes
- Si > 10 secondes, contacter l'équipe backend

---

## 🎯 Checklist d'intégration

- [ ] Récupérer l'URL de l'API auprès de l'équipe backend
- [ ] Récupérer les credentials (email/password)
- [ ] Tester l'API avec curl ou Postman
- [ ] Créer le service d'authentification
- [ ] Créer le service d'analyse
- [ ] Implémenter l'upload de fichier
- [ ] Afficher les résultats
- [ ] Gérer les erreurs
- [ ] Tester avec différents formats (PDF, DOCX)
- [ ] Valider la taille max des fichiers (10MB)

---

**Vous êtes prêt! Bon développement! 🚀**

Pour toute question, contactez l'équipe backend qui maintient l'API.
