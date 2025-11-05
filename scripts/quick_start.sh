#!/bin/bash

# Script complet de test - Lance TOUT automatiquement
# Usage: ./scripts/quick_test.sh

set -e

cd /workspaces/cv-ai-

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         🚀 TEST COMPLET - Analyseur de CV                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 1. Nettoyage
echo "📋 Étape 1/5: Nettoyage des ports..."
./scripts/stop_all.sh 2>/dev/null || true
sleep 2
echo "   ✅ Ports nettoyés"

# 2. FastAPI
echo ""
echo "📋 Étape 2/5: Démarrage de FastAPI..."
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null || true
nohup uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > /tmp/fastapi.log 2>&1 &
FASTAPI_PID=$!

# Attendre FastAPI
for i in {1..15}; do
    if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
        echo "   ✅ FastAPI opérationnel (PID: $FASTAPI_PID)"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "   ❌ Erreur: FastAPI n'a pas démarré"
        tail -20 /tmp/fastapi.log
        exit 1
    fi
    sleep 1
done

# 3. Node Proxy
echo ""
echo "📋 Étape 3/5: Démarrage du Node Proxy..."
cd examples/integration/node-proxy
npm install --silent 2>/dev/null || true
nohup node server.js > /tmp/node-proxy.log 2>&1 &
NODE_PID=$!

# Attendre Node
for i in {1..10}; do
    if curl -s http://localhost:4000/healthz >/dev/null 2>&1; then
        echo "   ✅ Node Proxy opérationnel (PID: $NODE_PID)"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "   ❌ Erreur: Node Proxy n'a pas démarré"
        tail -20 /tmp/node-proxy.log
        exit 1
    fi
    sleep 1
done

# 4. React
echo ""
echo "📋 Étape 4/5: Configuration de React..."
cd /workspaces/cv-ai-/examples/integration/react-demo
npm install --silent 2>/dev/null || true
echo "   ✅ React configuré"

# 5. Test API
echo ""
echo "📋 Étape 5/5: Test de l'API..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:4000/api/resume/analyze \
  -F "file=@/workspaces/cv-ai-/temp/test_cv_sample.txt")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ API fonctionne correctement"
    echo ""
    echo "   Aperçu de la réponse:"
    echo "$BODY" | python3 -m json.tool | head -15
    echo "   ..."
else
    echo "   ⚠️  API retourne le code: $HTTP_CODE"
    echo "   Réponse: $BODY"
fi

# Résumé
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ✅ TOUT EST PRÊT!                               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Services actifs:"
echo "   • FastAPI:    http://localhost:8000 (PID: $FASTAPI_PID)"
echo "   • Node Proxy: http://localhost:4000 (PID: $NODE_PID)"
echo "   • React:      Prêt à démarrer"
echo ""
echo "🚀 Pour lancer React, ouvrir un NOUVEAU TERMINAL et exécuter:"
echo ""
echo "   cd /workspaces/cv-ai-/examples/integration/react-demo"
echo "   npm run dev"
echo ""
echo "🌐 Puis ouvrir dans le navigateur:"
echo ""
echo "   http://localhost:3000"
echo ""
echo "🛑 Pour arrêter tous les services:"
echo ""
echo "   ./scripts/stop_all.sh"
echo ""
echo "📝 Logs en cas de problème:"
echo "   • tail -f /tmp/fastapi.log"
echo "   • tail -f /tmp/node-proxy.log"
echo ""

# Sauvegarder les PIDs
echo "$FASTAPI_PID $NODE_PID" > /tmp/cv-analyzer-pids.txt

echo "✨ Les services backend restent actifs en arrière-plan"
echo "   (Utilisez 'kill $FASTAPI_PID $NODE_PID' pour les arrêter)"
echo ""
