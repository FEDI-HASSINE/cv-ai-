# React ↔ Node ↔ FastAPI (exemple minimal)

Ce dossier contient un composant React `App.jsx` montrant comment envoyer un fichier CV
vers un proxy Node, qui lui-même appelle l'API FastAPI du projet.

## Schéma

React (localhost:5173/3000) → Node Proxy (localhost:4000) → FastAPI (localhost:8000)

## Pré-requis
- FastAPI lancé (voir docs/FASTAPI_SETUP.md)
- Node proxy lancé (voir `../node-proxy`)
- Une appli React/Vite existante dans laquelle coller `App.jsx` (ou créer rapidement une app Vite)

## Intégration rapide

1) Démarrez l'API FastAPI

```bash
./scripts/start_api.sh 8000
```

2) Configurez et démarrez le proxy Node

```bash
cd ../../integration/node-proxy
cp .env.example .env
# Éditez .env si besoin (FASTAPI_URL, API_TOKEN ou API_EMAIL/API_PASSWORD)
npm install
npm run dev
```

3) Ajoutez `App.jsx` dans votre projet React et montez-le dans votre arbre de composants.
Par exemple, dans Vite, remplacez `src/App.jsx` par le contenu de ce fichier, puis lancez :

```bash
npm run dev
```

4) Ouvrez http://localhost:5173 (ou 3000) et testez l’upload d’un fichier .pdf/.docx.

> Note: Le proxy Node gère l’authentification auprès de FastAPI (porteur d’un token via `/api/v1/auth/login`).
> Vous pouvez aussi fournir `API_TOKEN` directement dans `.env` du proxy.
