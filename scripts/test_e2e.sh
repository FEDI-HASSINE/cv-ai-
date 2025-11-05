#!/usr/bin/env bash

set -euo pipefail

echo "🚀 Script de test end-to-end pour l'analyseur de CV"
echo "=================================================="
echo

# Colors
GREEN='\033[0.32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Ports
FASTAPI_PORT=8000
NODE_PORT=4000
REACT_PORT=3000

PROJECT_ROOT="/workspaces/cv-ai-"

echo "📋 Prérequis:"
echo "  - Python 3.x avec pip"
echo "  - Node.js et npm"
echo "  - Ports ${FASTAPI_PORT}, ${NODE_PORT}, ${REACT_PORT} disponibles"
echo

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_wait=30
    local count=0
    
    echo -n "Attente de $name "
    while [ $count -lt $max_wait ]; do
        if curl -s -f "$url" >/dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
        count=$((count + 1))
    done
    echo -e " ${RED}✗${NC}"
    return 1
}

echo "Étape 1: Installation des dépendances Python"
echo "--------------------------------------------"
cd "$PROJECT_ROOT"

# Create temporary venv if needed
if [ ! -d "venv" ]; then
    echo "Création du venv..."
    python3 -m venv venv || { echo -e "${RED}Erreur: impossible de créer venv${NC}"; exit 1; }
fi

echo "Installation des dépendances FastAPI..."
./venv/bin/pip install -q --upgrade pip
./venv/bin/pip install -q fastapi==0.115.2 uvicorn==0.30.6 python-multipart==0.0.19 \
    pydantic==2.9.2 cryptography==42.0.4 python-jose==3.3.0 passlib==1.7.4 \
    python-dotenv==1.0.0 PyPDF2 python-docx pandas

echo -e "${GREEN}✓${NC} Dépendances Python installées"
echo

echo "Étape 2: Démarrage de FastAPI"
echo "-----------------------------"
if check_port $FASTAPI_PORT; then
    echo -e "${YELLOW}⚠${NC} Port $FASTAPI_PORT déjà utilisé, nettoyage..."
    lsof -ti:$FASTAPI_PORT | xargs kill -9 2>/dev/null || true
    sleep 2
fi

nohup ./venv/bin/python -m uvicorn src.api.main:app \
    --host 0.0.0.0 --port $FASTAPI_PORT --reload \
    >/tmp/fastapi-test.log 2>&1 &
FASTAPI_PID=$!
echo "FastAPI PID: $FASTAPI_PID"

if wait_for_service "http://127.0.0.1:$FASTAPI_PORT/api/v1/health" "FastAPI"; then
    echo -e "${GREEN}✓${NC} FastAPI est opérationnel sur http://localhost:$FASTAPI_PORT"
else
    echo -e "${RED}✗${NC} FastAPI n'a pas démarré"
    echo "Logs FastAPI:"
    tail -20 /tmp/fastapi-test.log
    exit 1
fi
echo

echo "Étape 3: Configuration et démarrage du proxy Node"
echo "------------------------------------------------"
cd "$PROJECT_ROOT/examples/integration/node-proxy"

if [ ! -f ".env" ]; then
    echo "Création du fichier .env..."
    cat > .env <<EOF
FASTAPI_URL=http://localhost:$FASTAPI_PORT
API_EMAIL=admin@example.com
API_PASSWORD=admin123
PROXY_CORS_ORIGINS=http://localhost:$REACT_PORT,http://localhost:5173
EOF
fi

if [ ! -d "node_modules" ]; then
    echo "Installation des dépendances npm..."
    npm install --silent
fi

if check_port $NODE_PORT; then
    echo -e "${YELLOW}⚠${NC} Port $NODE_PORT déjà utilisé, nettoyage..."
    lsof -ti:$NODE_PORT | xargs kill -9 2>/dev/null || true
    sleep 2
fi

nohup npm run dev >/tmp/node-proxy-test.log 2>&1 &
NODE_PID=$!
echo "Node Proxy PID: $NODE_PID"

if wait_for_service "http://127.0.0.1:$NODE_PORT/healthz" "Node Proxy"; then
    echo -e "${GREEN}✓${NC} Node Proxy est opérationnel sur http://localhost:$NODE_PORT"
else
    echo -e "${RED}✗${NC} Node Proxy n'a pas démarré"
    echo "Logs Node Proxy:"
    tail -20 /tmp/node-proxy-test.log
    kill $FASTAPI_PID 2>/dev/null || true
    exit 1
fi
echo

echo "Étape 4: Configuration de l'interface React"
echo "-------------------------------------------"
cd "$PROJECT_ROOT/examples/integration/react-demo"

if [ ! -f ".env" ]; then
    echo "Création du fichier .env..."
    cat > .env <<EOF
REACT_APP_BACKEND_URL=http://localhost:$NODE_PORT
EOF
fi

if [ ! -d "node_modules" ]; then
    echo "Installation des dépendances npm..."
    npm install --silent
fi

echo -e "${GREEN}✓${NC} Interface React configurée"
echo

echo "=================================================="
echo -e "${GREEN}✅ Tous les services sont démarrés!${NC}"
echo "=================================================="
echo
echo "📍 URLs des services:"
echo "  - FastAPI Docs:    http://localhost:$FASTAPI_PORT/api/docs"
echo "  - FastAPI Health:  http://localhost:$FASTAPI_PORT/api/v1/health"
echo "  - Node Proxy:      http://localhost:$NODE_PORT/healthz"
echo "  - React (à lancer): cd $PROJECT_ROOT/examples/integration/react-demo && npm run dev"
echo
echo "🧪 Test manuel:"
echo "  1. Lancer React: cd examples/integration/react-demo && npm run dev"
echo "  2. Ouvrir http://localhost:$REACT_PORT dans votre navigateur"
echo "  3. Uploader un fichier CV"
echo "  4. Vérifier les résultats d'analyse"
echo
echo "🛑 Arrêter les services:"
echo "  kill $FASTAPI_PID $NODE_PID"
echo
echo "📝 Logs:"
echo "  - FastAPI: tail -f /tmp/fastapi-test.log"
echo "  - Node Proxy: tail -f /tmp/node-proxy-test.log"
echo

# Keep script running to show logs
echo "Appuyez sur Ctrl+C pour arrêter tous les services..."
trap "echo '🛑 Arrêt des services...'; kill $FASTAPI_PID $NODE_PID 2>/dev/null; exit 0" INT TERM

# Wait for user interrupt
wait
