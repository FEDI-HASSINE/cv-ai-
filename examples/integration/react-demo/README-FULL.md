# Analyseur de CV - Interface React

Interface React moderne et professionnelle pour analyser des CV en utilisant FastAPI via un proxy Node.js.

## 🎯 Fonctionnalités

- **Upload de CV** : Support PDF, DOCX, DOC, TXT
- **Analyse en temps réel** : Communication React → Node → FastAPI
- **Affichage visuel** : 
  - Scores circulaires animés (Overall & ATS)
  - Badges de compétences techniques et soft skills
  - Listes de points forts, faiblesses et suggestions
  - Vue JSON brute pour debugging
- **Interface moderne** : Design responsive avec animations

## 🚀 Installation rapide

### Prérequis

1. **FastAPI** lancé sur port 8000
2. **Node proxy** lancé sur port 4000
3. Node.js et npm installés

### Étapes

```bash
# 1. Aller dans le dossier
cd examples/integration/react-demo

# 2. Configurer l'environnement
cp .env.example .env

# 3. Installer les dépendances
npm install

# 4. Lancer l'interface React (dev mode)
npm run dev
```

L'interface sera accessible sur **http://localhost:3000**

## 📋 Architecture complète

```
React (localhost:3000)
  ↓ POST /api/resume/analyze + file
Node Proxy (localhost:4000)
  ↓ POST /api/v1/resume/analyze + Bearer token
FastAPI (localhost:8000)
  ↓ Retourne JSON
Node Proxy
  ↓ Retourne JSON
React (affiche résultats)
```

## 🧪 Test end-to-end

### 1. Démarrer FastAPI

```bash
cd /workspaces/cv-ai-
./scripts/start_api.sh 8000
```

### 2. Démarrer le proxy Node

```bash
cd examples/integration/node-proxy
cp .env.example .env
# Configurez API_EMAIL/API_PASSWORD ou API_TOKEN dans .env
npm install
npm run dev
```

### 3. Démarrer React

```bash
cd examples/integration/react-demo
npm install
npm run dev
```

### 4. Tester dans le navigateur

1. Ouvrir http://localhost:3000
2. Uploader un fichier CV (PDF ou DOCX)
3. Cliquer sur "Analyser le CV"
4. Voir les résultats affichés en temps réel

## 📦 Structure des fichiers

```
react-demo/
├── index.html              # Point d'entrée HTML
├── package.json            # Dépendances npm
├── vite.config.js          # Config Vite
├── .env.example            # Variables d'environnement
└── src/
    ├── main.jsx            # Bootstrap React
    ├── App.jsx             # Composant principal
    └── App.css             # Styles modernes
```

## 🔧 Configuration

### Variables d'environnement (.env)

```bash
REACT_APP_BACKEND_URL=http://localhost:4000
```

## 📊 Format de réponse FastAPI

```json
{
  "overall_score": 75,
  "ats_score": 82,
  "technical_skills": ["Python", "React", "FastAPI"],
  "soft_skills": ["Leadership", "Communication"],
  "experience_years": 5.0,
  "strengths": ["Profil technique solide"],
  "weaknesses": ["Manque de certifications"],
  "suggestions": ["Ajouter une section certifications"]
}
```

## 🐛 Debugging

### Problème : Erreur CORS

Vérifiez que le proxy Node a `PROXY_CORS_ORIGINS` configuré :

```bash
PROXY_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Problème : Token invalide

Vérifiez les credentials dans `.env` du proxy Node :

```bash
API_EMAIL=admin@example.com
API_PASSWORD=admin123
```

## 📖 Commandes disponibles

- `npm run dev` : Lance le serveur de dev Vite
- `npm run build` : Build pour production
- `npm run preview` : Prévisualise le build
