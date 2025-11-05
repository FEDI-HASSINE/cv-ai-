# 🧹 Guide d'Optimisation Mémoire - CV Analyzer

## 📊 État Actuel du Disque

```bash
df -h | grep /workspaces
```

**Objectif**: Maintenir < 80% d'utilisation pour éviter les problèmes

---

## 🚨 Nettoyage Rapide (Mode Normal)

Pour nettoyer les caches sans toucher aux dépendances:

```bash
./scripts/cleanup.sh
```

**Supprime:**
- ✓ `__pycache__/` et `.pyc`
- ✓ Logs temporaires
- ✓ Fichiers PDF/DOCX inutiles
- ✓ `.pytest_cache`
- ✓ Caches système (~4GB)

**Conserve:**
- ✓ `venv/` (Python)
- ✓ `node_modules/` (Node)

---

## 🔥 Nettoyage Agressif (Libère Tout)

Pour libérer le maximum d'espace:

```bash
./scripts/cleanup.sh --aggressive
```

**Supprime TOUT:**
- ✓ Caches système (~4GB)
- ✓ `venv/` (~3GB)
- ✓ `node_modules/` (~56MB)
- ✓ Tous fichiers temporaires

**Total libéré: ~7GB**

---

## 🔄 Réinstallation Rapide

Après nettoyage agressif, réinstaller uniquement le minimum:

### 1. Python (minimal - 200MB au lieu de 3GB)

```bash
cd /workspaces/cv-ai-
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.minimal.txt
```

### 2. Node Proxy (8MB)

```bash
cd examples/integration/node-proxy
npm install --production
```

### 3. React (47MB)

```bash
cd examples/integration/react-demo
npm install
```

**Total après réinstallation: ~255MB** (vs 3GB avant)

---

## 📉 Optimisations Permanentes

### 1. Utiliser requirements.minimal.txt

Au lieu de `requirements.txt` (3GB), utiliser `requirements.minimal.txt` (200MB):

```bash
pip install -r requirements.minimal.txt
```

**Inclus uniquement:**
- FastAPI + Uvicorn
- Pydantic
- PyPDF2 + python-docx
- JWT/Crypto minimal

**Exclut (commenté):**
- OpenAI SDK
- pandas/numpy
- sentence-transformers
- spacy

### 2. npm install --production

Pour Node, installer sans devDependencies:

```bash
npm install --production
```

### 3. Nettoyer régulièrement

Ajouter à votre routine:

```bash
# Tous les jours
rm -rf ~/.cache/*
npm cache clean --force

# Toutes les semaines
./scripts/cleanup.sh --aggressive
```

---

## 📊 Taille des Composants

| Composant | Normal | Optimisé | Économie |
|-----------|--------|----------|----------|
| venv Python | 3.0 GB | 200 MB | 2.8 GB |
| node_modules | 56 MB | 8 MB* | 48 MB |
| Caches | 4.2 GB | 0 MB | 4.2 GB |
| **TOTAL** | **7.3 GB** | **208 MB** | **7.1 GB** |

*Avec `--production`

---

## 🎯 Checklist Quotidienne

Avant de commencer à travailler:

```bash
# 1. Vérifier l'espace
df -h | grep /workspaces

# 2. Si > 85%, nettoyer
./scripts/cleanup.sh

# 3. Si > 95%, mode agressif
./scripts/cleanup.sh --aggressive
```

---

## 🔍 Commandes de Diagnostic

### Trouver les plus gros fichiers:

```bash
du -sh /workspaces/cv-ai-/* | sort -hr | head -20
```

### Trouver les caches cachés:

```bash
find ~ -type d -name "__pycache__" -o -name "node_modules" -o -name ".cache" 2>/dev/null | head -20
```

### Espace par type de fichier:

```bash
find /workspaces/cv-ai- -type f -name "*.pyc" -exec du -ch {} + | tail -1
find /workspaces/cv-ai- -type f -name "*.log" -exec du -ch {} + | tail -1
```

---

## 🚀 Configuration Optimale pour Production

### .gitignore (déjà configuré)

```gitignore
venv/
node_modules/
__pycache__/
*.pyc
*.log
.cache/
temp/
*.pdf
*.docx
```

### .dockerignore (si vous utilisez Docker)

```dockerignore
venv/
node_modules/
__pycache__/
*.pyc
.git/
temp/
logs/
```

---

## ⚡ Scripts Utiles

### Nettoyage automatique au démarrage:

Ajouter dans `~/.bashrc`:

```bash
# Nettoyer cache au login
if [ -d ~/.cache ]; then
    CACHE_SIZE=$(du -sh ~/.cache 2>/dev/null | cut -f1)
    if [ "$CACHE_SIZE" != "0" ]; then
        echo "🧹 Cache détecté: $CACHE_SIZE - Nettoyage..."
        rm -rf ~/.cache/* 2>/dev/null
    fi
fi
```

### Surveillance de l'espace:

```bash
# Créer un alias
alias diskcheck='df -h | grep /workspaces && echo "" && du -sh /workspaces/cv-ai-'
```

---

## 🎯 Objectifs de Performance

| Métrique | Cible | Critique |
|----------|-------|----------|
| Espace disque | < 80% | > 95% |
| Taille projet | < 300 MB | > 3 GB |
| Cache système | < 500 MB | > 4 GB |
| venv Python | < 500 MB | > 3 GB |

---

## 📝 Notes Importantes

1. **Toujours sauvegarder** avant nettoyage agressif
2. **Tester après réinstallation** que tout fonctionne
3. **Documenter** les dépendances vraiment nécessaires
4. **Monitorer** l'espace disque régulièrement

---

## 🆘 En Cas d'Urgence (Disque à 100%)

Si vous voyez `ENOSPC: no space left on device`:

```bash
# 1. ARRÊTER TOUT
cd /workspaces/cv-ai-
./scripts/stop_all.sh

# 2. NETTOYAGE MAXIMUM
rm -rf venv node_modules ~/.cache/*
npm cache clean --force

# 3. VÉRIFIER
df -h | grep /workspaces

# 4. RÉINSTALLER MINIMAL
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.minimal.txt
```

---

**✅ Avec ces optimisations, vous pouvez réduire l'utilisation de 7GB à 300MB!**
