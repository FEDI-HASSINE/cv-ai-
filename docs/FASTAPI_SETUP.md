# FastAPI — Mise en place et intégration React/Node

Cette page explique comment démarrer l’API FastAPI localement, configurer CORS, et l’utiliser via un proxy Node avec un frontend React.

## Démarrage rapide

- Prérequis Python: `fastapi`, `uvicorn`, `python-multipart` sont déjà listés dans `requirements.txt`.
- Utilisez le script:

```bash
./scripts/start_api.sh 8000
```

L’API sera disponible sur http://localhost:8000 avec la documentation Swagger sur http://localhost:8000/api/docs.

## CORS

Les origines autorisées sont configurables via la variable d’environnement `CORS_ORIGINS` (liste séparée par des virgules).
Par défaut, les origines suivantes sont autorisées:
- http://localhost:3000 (CRA)
- http://localhost:5173 (Vite)
- http://localhost:8501 (Streamlit)
- https://utopiahire.com (prod)

Exemple pour autoriser une origine supplémentaire:

```bash
export CORS_ORIGINS="http://localhost:3000,http://localhost:5173,http://localhost:8501,http://localhost:8080"
./scripts/start_api.sh 8000
```

## Authentification (JWT simplifié)

- Endpoint de login: `POST /api/v1/auth/login` avec `{ email, password }`.
- Pour démo: tout mot de passe ≥ 8 caractères est accepté (à remplacer en prod).
- Les endpoints `POST /api/v1/resume/analyze` et `POST /api/v1/resume/rewrite` exigent `Authorization: Bearer <token>`.

## Proxy Node (recommandé pour projets React)

Un exemple de proxy est fourni dans `examples/integration/node-proxy`.

- Configurez-le via `.env`:
  - `FASTAPI_URL=http://localhost:8000`
  - `API_TOKEN=<facultatif>` ou couple `API_EMAIL`/`API_PASSWORD` pour que le proxy récupère un token automatiquement via `/auth/login`.
- Lancez-le:

```bash
cd examples/integration/node-proxy
cp .env.example .env
npm install
npm run dev
```

Le proxy écoute par défaut sur http://localhost:4000 et expose:
- `POST /api/resume/analyze` (multipart/form-data: file)
- `POST /api/resume/rewrite` (multipart/form-data: file, query `use_ai` optionnelle)

## Frontend React — exemple minimal

Un composant prêt à l’emploi est dans `examples/integration/react-demo/App.jsx`.
Il envoie un fichier au proxy Node et affiche la réponse JSON.

Schéma: React → Node Proxy → FastAPI.

## Déploiement — points d’attention

- Protéger réellement l’auth (DB, hashing, RBAC) au lieu du placeholder.
- Déporter le rate limiting sur Redis/Nginx en prod.
- Restreindre CORS aux domaines nécessaires.
- Mettre derrière un reverse proxy (Nginx/Caddy) avec TLS.
- Sur FastAPI, envisager des workers (`uvicorn --workers 2` ou Gunicorn+Uvicorn).
