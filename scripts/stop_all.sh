#!/bin/bash

# Script pour arrêter tous les services
# Usage: ./scripts/stop_all.sh

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Arrêt de tous les services CV Analyzer${NC}"

# Arrêter par PIDs sauvegardés
if [ -f /tmp/cv-analyzer-pids.txt ]; then
    PIDS=$(cat /tmp/cv-analyzer-pids.txt)
    echo "Arrêt des processus: $PIDS"
    kill $PIDS 2>/dev/null
    rm -f /tmp/cv-analyzer-pids.txt
fi

# Nettoyage complet des ports
echo "Nettoyage des ports 3000, 4000, 8000..."
lsof -ti:3000,4000,8000 | xargs kill -9 2>/dev/null || true

sleep 1

# Vérification
RUNNING=0
for port in 3000 4000 8000; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo -e "⚠️  Port $port encore occupé"
        RUNNING=1
    fi
done

if [ $RUNNING -eq 0 ]; then
    echo -e "${GREEN}✓ Tous les services arrêtés${NC}"
else
    echo -e "${YELLOW}⚠️  Certains ports sont encore utilisés${NC}"
fi
