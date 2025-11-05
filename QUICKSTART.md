# 🚀 Guide de Lancement Rapide - Analyseur de CV

Guide complet pour lancer et tester l'application React → Node → FastAPI

## 📋 Option 1: Script Automatique (Recommandé)

### Lancement en une commande

```bash
cd /workspaces/cv-ai-
./scripts/test_e2e.sh
```

Ce script va:
1. ✅ Installer toutes les dépendances Python
2. ✅ Démarrer FastAPI sur port 8000
3. ✅ Démarrer le proxy Node sur port 4000
4. ✅ Configurer l'interface React
5. ✅ Afficher les URLs et instructions

### Ensuite, lancer React manuellement

Dans un **nouveau terminal**:

```bash
cd /workspaces/cv-ai-/examples/integration/react-demo
npm run dev
```

Ouvrir **http://localhost:3000** dans votre navigateur.

---

## 📋 Option 2: Lancement Manuel

### Étape 1: FastAPI (Terminal 1)

```bash
cd /workspaces/cv-ai-

# Créer venv si nécessaire
python3 -m venv venv

# Installer dépendances
./venv/bin/pip install -U pip
./venv/bin/pip install fastapi uvicorn python-multipart pydantic \
    cryptography python-jose passlib python-dotenv PyPDF2 python-docx pandas

# Lancer FastAPI
./venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

✅ **Vérification**: http://localhost:8000/api/docs

### Étape 2: Proxy Node (Terminal 2)

```bash
cd /workspaces/cv-ai-/examples/integration/node-proxy

# Configurer
cp .env.example .env
# Éditer .env si nécessaire (API_EMAIL/API_PASSWORD)

# Installer et lancer
npm install
npm run dev
```

✅ **Vérification**: http://localhost:4000/healthz

### Étape 3: Interface React (Terminal 3)

```bash
cd /workspaces/cv-ai-/examples/integration/react-demo

# Configurer
cp .env.example .env

# Installer et lancer
npm install
npm run dev
```

✅ **Ouvrir**: http://localhost:3000

---

## 🧪 Test Complet

1. **Ouvrir l'interface** : http://localhost:3000

2. **Uploader un CV** : 
   - Cliquer sur "Choisir un fichier CV"
   - Sélectionner un fichier PDF ou DOCX
   - Exemple de test: `/workspaces/cv-ai-/utopia.pdf` (si disponible)

3. **Analyser** :
   - Cliquer sur "Analyser le CV"
   - Attendre l'analyse (quelques secondes)

4. **Vérifier les résultats** :
   - ✅ Score Global (cercle animé)
   - ✅ Score ATS (cercle animé)
   - ✅ Années d'expérience
   - ✅ Compétences techniques (badges bleus)
   - ✅ Soft skills (badges roses)
   - ✅ Points forts
   - ✅ Points à améliorer
   - ✅ Suggestions d'amélioration
   - ✅ JSON brut (section dépliable)

---

## 🔍 Flux de Données

```
1. Utilisateur uploade CV.pdf dans React (localhost:3000)
   ↓
2. React POST /api/resume/analyze → Node Proxy (localhost:4000)
   ↓
3. Node Proxy:
   - Appelle /api/v1/auth/login sur FastAPI (obtient JWT)
   - POST /api/v1/resume/analyze + Bearer token → FastAPI (localhost:8000)
   ↓
4. FastAPI:
   - Parse le PDF/DOCX
   - Analyse le contenu
   - Retourne JSON avec scores, compétences, suggestions
   ↓
5. Node Proxy retourne JSON → React
   ↓
6. React affiche les résultats dans l'interface moderne
```

---

## 🐛 Debugging

### Problème: FastAPI ne démarre pas

```bash
# Vérifier les logs
tail -f /tmp/fastapi-test.log

# Vérifier le port
lsof -i :8000

# Tuer le processus si bloqué
lsof -ti :8000 | xargs kill -9
```

### Problème: Node Proxy erreur CORS

Éditer `/workspaces/cv-ai-/examples/integration/node-proxy/.env`:

```bash
PROXY_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Puis redémarrer le proxy Node.

### Problème: "Cannot extract text from file"

Vérifier que les dépendances de parsing sont installées:

```bash
./venv/bin/pip install PyPDF2 python-docx
```

### Problème: "Unauthorized" (401)

Le proxy Node n'arrive pas à s'authentifier. Vérifier dans `.env` du proxy:

```bash
# Option 1: Credentials
API_EMAIL=admin@example.com
API_PASSWORD=admin123

# Option 2: Token statique (préféré)
API_TOKEN=votre_jwt_token
```

Pour obtenir un token manuellement:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

Copier le `access_token` dans `API_TOKEN`.

---

## 📊 Structure de la Réponse JSON

```json
{
  "overall_score": 75,
  "ats_score": 82,
  "technical_skills": ["Python", "React", "FastAPI", "Docker"],
  "soft_skills": ["Leadership", "Communication", "Teamwork"],
  "experience_years": 5.0,
  "strengths": [
    "Profil technique solide avec expérience diversifiée",
    "Bonne maîtrise des technologies modernes"
  ],
  "weaknesses": [
    "Manque de certifications professionnelles",
    "Peu de contributions open source visibles"
  ],
  "suggestions": [
    "Ajouter une section certifications (AWS, Azure, etc.)",
    "Quantifier les réalisations avec des métriques précises",
    "Inclure des liens vers projets GitHub ou portfolio"
  ]
}
```

---

## 📝 Logs Utiles

```bash
# FastAPI
tail -f /tmp/fastapi-test.log

# Node Proxy
tail -f /tmp/node-proxy-test.log

# Ou avec script automatique
./scripts/test_e2e.sh
# (les logs s'affichent en direct)
```

---

## 🛑 Arrêt Propre

### Si lancé avec le script automatique

Appuyez sur **Ctrl+C** dans le terminal du script.

### Si lancé manuellement

Dans chaque terminal:
- **Ctrl+C** pour arrêter le processus

Ou tuer tous les processus:

```bash
lsof -ti :8000 | xargs kill -9  # FastAPI
lsof -ti :4000 | xargs kill -9  # Node Proxy
lsof -ti :3000 | xargs kill -9  # React (si lancé via npm run dev)
```

---

## 🎨 Personnalisation

### Changer le port React

Éditer `examples/integration/react-demo/vite.config.js`:

```js
export default defineConfig({
  server: {
    port: 5173  // Changer ici
  }
})
```

### Changer les couleurs de l'interface

Éditer `examples/integration/react-demo/src/App.css`:

```css
:root {
  --primary: #6366f1;      /* Couleur principale */
  --success: #10b981;      /* Vert */
  --warning: #f59e0b;      /* Orange */
  --danger: #ef4444;       /* Rouge */
}
```

---

## ✅ Checklist de Validation

- [ ] FastAPI répond sur http://localhost:8000/api/docs
- [ ] FastAPI health check 200: http://localhost:8000/api/v1/health
- [ ] Node Proxy répond: http://localhost:4000/healthz
- [ ] React affiche l'interface: http://localhost:3000
- [ ] Upload d'un CV fonctionne
- [ ] Résultats affichés correctement
- [ ] Scores circulaires animés visibles
- [ ] Compétences en badges affichées
- [ ] Points forts/faiblesses/suggestions listés
- [ ] JSON brut accessible (section dépliable)

---

## 🤝 Support

En cas de problème:

1. Vérifier les logs (voir section Logs ci-dessus)
2. Vérifier les ports avec `lsof -i :<port>`
3. Tester chaque service individuellement
4. Consulter les README détaillés dans chaque dossier

**Bonne analyse!** 🎯
