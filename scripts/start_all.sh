#!/bin/bash

# Script pour démarrer tous les services sur les bons ports
# Usage: ./scripts/start_all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Démarrage de tous les services CV Analyzer${NC}"
echo "=================================================="

# 1. Nettoyer tous les ports
echo -e "\n${YELLOW}📌 Étape 1: Nettoyage des ports${NC}"
lsof -ti:3000,4000,8000 | xargs kill -9 2>/dev/null || true
sleep 1
echo -e "${GREEN}✓ Ports nettoyés${NC}"

# 2. Vérifier les ports
echo -e "\n${YELLOW}📌 Étape 2: Vérification des ports${NC}"
for port in 3000 4000 8000; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $port encore occupé${NC}"
        exit 1
    else
        echo -e "${GREEN}✓ Port $port libre${NC}"
    fi
done

# 3. Installer/créer venv Python si nécessaire
echo -e "\n${YELLOW}📌 Étape 3: Configuration Python${NC}"
cd "$PROJECT_ROOT"
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel Python..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Environnement Python prêt${NC}"

# 4. Démarrer FastAPI
echo -e "\n${YELLOW}📌 Étape 4: Démarrage de FastAPI (port 8000)${NC}"
nohup ./venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > /tmp/fastapi.log 2>&1 &
FASTAPI_PID=$!
echo "FastAPI PID: $FASTAPI_PID"

# Attendre FastAPI
for i in {1..30}; do
    if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓ FastAPI opérationnel${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ FastAPI n'a pas démarré${NC}"
        tail -20 /tmp/fastapi.log
        exit 1
    fi
    sleep 1
done

# 5. Configurer et démarrer Node Proxy
echo -e "\n${YELLOW}📌 Étape 5: Démarrage du Node Proxy (port 4000)${NC}"
cd "$PROJECT_ROOT/examples/integration/node-proxy"

# Vérifier .env
if [ ! -f .env ]; then
    cat > .env <<EOF
FASTAPI_URL=http://127.0.0.1:8000
API_EMAIL=demo@example.com
API_PASSWORD=demopass123
PROXY_CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173
EOF
    echo "Fichier .env créé"
fi

# Installer dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    npm install
fi

nohup node server.js > /tmp/node-proxy.log 2>&1 &
NODE_PID=$!
echo "Node Proxy PID: $NODE_PID"

# Attendre Node Proxy
for i in {1..20}; do
    if curl -s http://localhost:4000/healthz >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Node Proxy opérationnel${NC}"
        break
    fi
    if [ $i -eq 20 ]; then
        echo -e "${RED}❌ Node Proxy n'a pas démarré${NC}"
        tail -20 /tmp/node-proxy.log
        exit 1
    fi
    sleep 1
done

# 6. Configurer React (sans le démarrer)
echo -e "\n${YELLOW}📌 Étape 6: Configuration React${NC}"
cd "$PROJECT_ROOT/examples/integration/react-demo"

# Vérifier .env
if [ ! -f .env ]; then
    echo "REACT_APP_BACKEND_URL=http://localhost:4000" > .env
    echo "Fichier .env créé"
fi

# Installer dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    npm install
fi

echo -e "${GREEN}✓ React configuré${NC}"

# 7. Instructions finales
echo ""
echo "=================================================="
echo -e "${GREEN}✅ Services backend démarrés avec succès!${NC}"
echo "=================================================="
echo ""
echo -e "${BLUE}📍 URLs:${NC}"
echo "  🔹 FastAPI:      http://localhost:8000/api/docs"
echo "  🔹 Health Check: http://localhost:8000/api/v1/health"
echo "  🔹 Node Proxy:   http://localhost:4000/healthz"
echo ""
echo -e "${BLUE}🚀 Pour démarrer React:${NC}"
echo "  cd $PROJECT_ROOT/examples/integration/react-demo"
echo "  npm run dev"
echo ""
echo -e "${BLUE}🌐 Puis ouvrir:${NC}"
echo "  http://localhost:3000"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo "  FastAPI:     tail -f /tmp/fastapi.log"
echo "  Node Proxy:  tail -f /tmp/node-proxy.log"
echo ""
echo -e "${BLUE}🛑 Arrêter les services:${NC}"
echo "  kill $FASTAPI_PID $NODE_PID"
echo ""
echo -e "${YELLOW}💡 Conseil: Gardez ce terminal ouvert et lancez React dans un nouveau terminal${NC}"
echo ""

# Sauvegarder les PIDs pour arrêt facile
echo "$FASTAPI_PID $NODE_PID" > /tmp/cv-analyzer-pids.txt

# Attendre Ctrl+C
trap "echo -e '\n${YELLOW}Arrêt des services...${NC}'; kill $FASTAPI_PID $NODE_PID 2>/dev/null; rm -f /tmp/cv-analyzer-pids.txt; echo -e '${GREEN}✓ Services arrêtés${NC}'; exit 0" INT TERM

echo "Appuyez sur Ctrl+C pour arrêter tous les services..."
wait
