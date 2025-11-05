# 🚀 Commandes à Exécuter - Test Complet de l'Interface

## 📋 Prérequis
Avoir 2 terminaux ouverts (Terminal 1 et Terminal 2)

---

## TERMINAL 1 - Services Backend

### Étape 1: Nettoyer les ports
```bash
cd /workspaces/cv-ai-
./scripts/stop_all.sh
```

### Étape 2: Démarrer FastAPI
```bash
cd /workspaces/cv-ai-
source venv/bin/activate
nohup uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > /tmp/fastapi.log 2>&1 &
echo "FastAPI PID: $!"
```

### Étape 3: Attendre 3 secondes et vérifier FastAPI
```bash
sleep 3
curl http://localhost:8000/api/v1/health
```

**Résultat attendu:** JSON avec `"status": "healthy"`

### Étape 4: Démarrer Node Proxy
```bash
cd /workspaces/cv-ai-/examples/integration/node-proxy
nohup node server.js > /tmp/node-proxy.log 2>&1 &
echo "Node Proxy PID: $!"
```

### Étape 5: Attendre 2 secondes et vérifier Node Proxy
```bash
sleep 2
curl http://localhost:4000/healthz
```

**Résultat attendu:** `{"ok":true}`

### ✅ Backend prêt!
**Gardez ce terminal ouvert** (ne pas fermer)

---

## TERMINAL 2 - Interface React

### Étape 1: Aller dans le dossier React
```bash
cd /workspaces/cv-ai-/examples/integration/react-demo
```

### Étape 2: Installer les dépendances (si pas déjà fait)
```bash
npm install
```

### Étape 3: Démarrer React
```bash
npm run dev
```

**Résultat attendu:**
```
VITE v5.4.21  ready in XXX ms

➜  Local:   http://localhost:3000/
```

### ✅ React prêt!
**Gardez ce terminal ouvert** (vous verrez les logs en temps réel)

---

## 🌐 NAVIGATEUR - Test de l'Interface

### Étape 1: Ouvrir l'interface
```
http://localhost:3000
```

### Étape 2: Vérifier l'affichage
Vous devriez voir:
- ✅ Titre "Analyseur de CV Intelligent"
- ✅ Zone d'upload avec icône
- ✅ Bouton "Choose File"
- ✅ Bouton "Analyser le CV"

### Étape 3: Tester l'upload
1. Cliquer sur "Choose File"
2. Sélectionner un fichier CV (PDF, DOCX ou TXT)
   - Fichier test disponible: `/workspaces/cv-ai-/temp/test_cv_sample.txt`
3. Cliquer sur "Analyser le CV"
4. Attendre quelques secondes

### Étape 4: Vérifier les résultats
Vous devriez voir s'afficher:
- ✅ Score Global (cercle animé)
- ✅ Score ATS (cercle animé)
- ✅ Badges de compétences techniques (bleu)
- ✅ Badges de compétences soft (rose)
- ✅ Liste des points forts
- ✅ Liste des points à améliorer
- ✅ Liste des suggestions
- ✅ Section JSON brute (dépliable en bas)

---

## 🧪 TEST MANUEL VIA CURL (Optionnel)

Si vous voulez tester l'API directement sans l'interface:

```bash
# Dans un nouveau terminal
cd /workspaces/cv-ai-

# Test avec le fichier exemple
curl -X POST http://localhost:4000/api/resume/analyze \
  -F "file=@temp/test_cv_sample.txt"
```

**Résultat attendu:** JSON complet avec scores, compétences, suggestions

---

## 🔍 VÉRIFICATION DES LOGS

Si quelque chose ne fonctionne pas:

### Voir les logs FastAPI:
```bash
tail -f /tmp/fastapi.log
```

### Voir les logs Node Proxy:
```bash
tail -f /tmp/node-proxy.log
```

### Voir les processus en cours:
```bash
lsof -ti:3000  # React
lsof -ti:4000  # Node Proxy
lsof -ti:8000  # FastAPI
```

---

## 🛑 ARRÊTER TOUS LES SERVICES

### Dans Terminal 2 (React):
Appuyez sur `Ctrl+C`

### Dans Terminal 1 ou nouveau terminal:
```bash
cd /workspaces/cv-ai-
./scripts/stop_all.sh
```

Ou manuellement:
```bash
# Trouver les PIDs
lsof -ti:8000,4000,3000

# Arrêter
kill $(lsof -ti:8000,4000,3000)
```

---

## ❌ RÉSOLUTION DE PROBLÈMES

### Problème: "Port already in use"
```bash
./scripts/stop_all.sh
# Puis relancer à partir de l'Étape 1
```

### Problème: "Cannot connect to backend"
Vérifier que Node Proxy tourne:
```bash
curl http://localhost:4000/healthz
```

### Problème: "401 Unauthorized"
Vérifier le fichier `.env` du proxy:
```bash
cat /workspaces/cv-ai-/examples/integration/node-proxy/.env
```

Doit contenir:
```
API_EMAIL=demo@example.com
API_PASSWORD=demopass123
```

### Problème: Interface React ne charge pas
1. Vérifier le port:
```bash
lsof -ti:3000
```

2. Vérifier la console du navigateur (F12)

3. Forcer le port dans `vite.config.js` (déjà fait normalement)

---

## 📊 CHECKLIST DE VALIDATION

Cochez au fur et à mesure:

**Backend:**
- [ ] FastAPI démarre sans erreur
- [ ] `curl http://localhost:8000/api/v1/health` retourne "healthy"
- [ ] Node Proxy démarre sans erreur
- [ ] `curl http://localhost:4000/healthz` retourne "ok"

**Frontend:**
- [ ] React démarre sur port 3000
- [ ] Interface s'affiche dans le navigateur
- [ ] Pas d'erreur dans la console (F12)

**Test Upload:**
- [ ] Peut sélectionner un fichier
- [ ] Bouton "Analyser" fonctionne
- [ ] Spinner de chargement s'affiche
- [ ] Résultats s'affichent après quelques secondes

**Résultats:**
- [ ] Scores affichés (0-100)
- [ ] Compétences en badges
- [ ] Listes de points forts/faiblesses
- [ ] Suggestions affichées
- [ ] JSON brut disponible

---

## 🎯 RÉCAPITULATIF RAPIDE

```bash
# Terminal 1 - Backend
cd /workspaces/cv-ai-
./scripts/stop_all.sh
source venv/bin/activate
nohup uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > /tmp/fastapi.log 2>&1 &
sleep 3
cd examples/integration/node-proxy
nohup node server.js > /tmp/node-proxy.log 2>&1 &
sleep 2

# Terminal 2 - Frontend
cd /workspaces/cv-ai-/examples/integration/react-demo
npm run dev

# Navigateur
# Ouvrir: http://localhost:3000
# Tester upload d'un CV
```

---

**🎉 Tout devrait fonctionner! Si vous avez des erreurs, consultez la section "Résolution de problèmes" ci-dessus.**
