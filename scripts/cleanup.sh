#!/bin/bash

# Script de nettoyage du projet
# Usage: ./scripts/cleanup.sh [--aggressive]

set -e

cd /workspaces/cv-ai-

AGGRESSIVE=false
if [ "$1" = "--aggressive" ]; then
    AGGRESSIVE=true
fi

echo "🧹 Nettoyage du projet CV Analyzer"
if [ "$AGGRESSIVE" = true ]; then
    echo "⚠️  MODE AGRESSIF: Suppression venv + node_modules"
fi
echo "===================================="
echo ""

# 1. Arrêter tous les services d'abord
echo "📋 Étape 1: Arrêt des services..."
./scripts/stop_all.sh 2>/dev/null || true
sleep 1
echo "   ✅ Services arrêtés"

# 2. Nettoyer __pycache__
echo ""
echo "📋 Étape 2: Suppression des fichiers __pycache__..."
PYCACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l)
if [ $PYCACHE_COUNT -gt 0 ]; then
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo "   ✅ $PYCACHE_COUNT dossiers __pycache__ supprimés"
else
    echo "   ℹ️  Aucun __pycache__ trouvé"
fi

# 3. Nettoyer fichiers .pyc
echo ""
echo "📋 Étape 3: Suppression des fichiers .pyc..."
PYC_COUNT=$(find . -type f -name "*.pyc" 2>/dev/null | wc -l)
if [ $PYC_COUNT -gt 0 ]; then
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    echo "   ✅ $PYC_COUNT fichiers .pyc supprimés"
else
    echo "   ℹ️  Aucun fichier .pyc trouvé"
fi

# 4. Nettoyer logs temporaires
echo ""
echo "📋 Étape 4: Nettoyage des logs temporaires..."
if [ -d "logs" ]; then
    rm -f logs/*.log 2>/dev/null || true
    echo "   ✅ Logs nettoyés"
fi
rm -f /tmp/fastapi*.log /tmp/node-proxy*.log 2>/dev/null || true
echo "   ✅ Logs /tmp nettoyés"

# 5. Nettoyer fichiers temporaires
echo ""
echo "📋 Étape 5: Suppression fichiers temporaires..."
rm -f nohup.out 2>/dev/null || true
rm -f /tmp/cv-analyzer-pids.txt 2>/dev/null || true
if [ -d "temp" ]; then
    # Garder test_cv_sample.txt
    find temp -type f ! -name "test_cv_sample.txt" -delete 2>/dev/null || true
fi
echo "   ✅ Fichiers temporaires nettoyés"

# 6. Nettoyer PDF inutiles (sauf échantillons)
echo ""
echo "📋 Étape 6: Nettoyage des fichiers PDF..."
if [ -f "utopia.pdf" ]; then
    rm -f utopia.pdf
    echo "   ✅ utopia.pdf supprimé"
else
    echo "   ℹ️  Pas de PDF inutile trouvé"
fi

# 7. Nettoyer node_modules (optionnel - à décommenter si besoin)
echo ""
if [ "$AGGRESSIVE" = true ]; then
    echo "📋 Étape 7: Suppression node_modules..."
    rm -rf examples/integration/node-proxy/node_modules
    rm -rf examples/integration/react-demo/node_modules
    echo "   ✅ node_modules supprimés (~56MB) - Relancer npm install"
else
    echo "📋 Étape 7: node_modules conservés"
    echo "   ℹ️  Pour supprimer: ./scripts/cleanup.sh --aggressive"
fi

# 8. Nettoyer venv Python (optionnel - à décommenter si besoin)
echo ""
if [ "$AGGRESSIVE" = true ]; then
    echo "📋 Étape 8: Suppression venv..."
    rm -rf venv
    echo "   ✅ venv supprimé (~3GB) - Relancer: python3 -m venv venv"
else
    echo "📋 Étape 8: venv conservé"
    echo "   ℹ️  Pour supprimer: ./scripts/cleanup.sh --aggressive"
fi

# 9. Nettoyer caches système
echo ""
echo "📋 Étape 9: Nettoyage caches système..."
CACHE_CLEANED=false
if [ -d "/home/codespace/.cache" ]; then
    CACHE_SIZE=$(du -sh /home/codespace/.cache 2>/dev/null | cut -f1)
    rm -rf /home/codespace/.cache/* 2>/dev/null || true
    echo "   ✅ Cache système supprimé ($CACHE_SIZE)"
    CACHE_CLEANED=true
fi
if [ -d "/home/codespace/.npm/_cacache" ]; then
    rm -rf /home/codespace/.npm/_cacache 2>/dev/null || true
    npm cache clean --force >/dev/null 2>&1 || true
    echo "   ✅ Cache npm nettoyé"
    CACHE_CLEANED=true
fi
if [ "$CACHE_CLEANED" = false ]; then
    echo "   ℹ️  Pas de cache à nettoyer"
fi

# 9. Nettoyer .pytest_cache
echo ""
echo "📋 Étape 10: Nettoyage caches pytest..."
if [ -d ".pytest_cache" ]; then
    rm -rf .pytest_cache
    echo "   ✅ .pytest_cache supprimé"
fi
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# 10. Afficher l'espace libéré
echo ""
echo "===================================="
echo "✅ Nettoyage terminé!"
echo "===================================="
echo ""
echo "📊 Espace disque:"
df -h | grep -E "Filesystem|/workspaces"
echo ""
echo "📊 Taille du projet:"
du -sh . 2>/dev/null
echo ""
echo "📁 Répartition (top 10):"
du -sh * 2>/dev/null | sort -hr | head -10
echo ""
if [ "$AGGRESSIVE" = true ]; then
    echo "⚠️  MODE AGRESSIF utilisé - Réinstallation requise:"
    echo "   • venv:         python3 -m venv venv && pip install -r requirements.minimal.txt"
    echo "   • node_modules: cd examples/integration/[node-proxy|react-demo] && npm install"
else
    echo "💡 Pour libérer plus d'espace:"
    echo "   ./scripts/cleanup.sh --aggressive"
fi
echo ""
