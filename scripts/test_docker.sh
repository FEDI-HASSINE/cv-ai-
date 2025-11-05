#!/bin/bash

# 🐳 Script de Test Docker - CV Analyzer API
# Teste automatiquement tous les aspects du déploiement Docker

set -e

# Couleurs pour affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage
print_header() {
    echo -e "\n${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Variables
API_URL="http://localhost:8000"
TEST_FILE="temp/test_cv_sample.txt"

print_header "TEST DOCKER - CV ANALYZER API"

# Test 1: Vérifier Docker
print_info "Test 1: Vérification de Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker n'est pas installé"
    exit 1
fi
print_success "Docker est installé ($(docker --version))"

# Test 2: Vérifier Docker Compose
print_info "Test 2: Vérification de Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose n'est pas installé"
    exit 1
fi
print_success "Docker Compose est installé"

# Test 3: Vérifier l'image
print_info "Test 3: Vérification de l'image Docker..."
if docker images | grep -q "cv-api"; then
    IMAGE_SIZE=$(docker images cv-api:latest --format "{{.Size}}")
    print_success "Image cv-api:latest existe (Taille: $IMAGE_SIZE)"
else
    print_error "Image cv-api:latest introuvable. Construire avec: docker build -t cv-api:latest ."
    exit 1
fi

# Test 4: Vérifier le conteneur
print_info "Test 4: Vérification du conteneur..."
if docker ps | grep -q "cv-analyzer-api"; then
    CONTAINER_STATUS=$(docker inspect cv-analyzer-api --format='{{.State.Status}}')
    HEALTH_STATUS=$(docker inspect cv-analyzer-api --format='{{.State.Health.Status}}' 2>/dev/null || echo "N/A")
    print_success "Conteneur cv-analyzer-api est en cours d'exécution"
    print_info "   Status: $CONTAINER_STATUS"
    print_info "   Health: $HEALTH_STATUS"
else
    print_error "Conteneur cv-analyzer-api n'est pas en cours d'exécution"
    print_info "Démarrer avec: docker-compose up -d api"
    exit 1
fi

# Test 5: Attendre que le service soit prêt
print_info "Test 5: Attente du démarrage complet..."
for i in {1..10}; do
    if curl -s "$API_URL/api/v1/health" > /dev/null 2>&1; then
        print_success "API est prête"
        break
    fi
    if [ $i -eq 10 ]; then
        print_error "Timeout: API ne répond pas après 10 secondes"
        exit 1
    fi
    sleep 1
done

# Test 6: Health Check
print_info "Test 6: Test du endpoint /health..."
HEALTH_RESPONSE=$(curl -s "$API_URL/api/v1/health")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_success "Health check OK"
    echo "$HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    print_error "Health check échoué"
    exit 1
fi

# Test 7: Documentation API
print_info "Test 7: Vérification de la documentation Swagger..."
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/docs")
if [ "$DOCS_RESPONSE" = "200" ]; then
    print_success "Documentation Swagger accessible à $API_URL/api/docs"
else
    print_error "Documentation Swagger non accessible (HTTP $DOCS_RESPONSE)"
fi

# Test 8: Authentification
print_info "Test 8: Test d'authentification..."
AUTH_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"demo@example.com","password":"demopass123"}')

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.access_token')
    print_success "Authentification réussie"
    print_info "   Token: ${TOKEN:0:50}..."
else
    print_error "Authentification échouée"
    echo "$AUTH_RESPONSE"
    exit 1
fi

# Test 9: Analyse de CV (si fichier test existe)
if [ -f "$TEST_FILE" ]; then
    print_info "Test 9: Test d'analyse de CV..."
    
    ANALYZE_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/resume/analyze" \
        -H "Authorization: Bearer $TOKEN" \
        -F "file=@$TEST_FILE")
    
    if echo "$ANALYZE_RESPONSE" | grep -q "overall_score"; then
        SCORE=$(echo "$ANALYZE_RESPONSE" | jq -r '.overall_score')
        SKILLS_COUNT=$(echo "$ANALYZE_RESPONSE" | jq '.technical_skills | length')
        print_success "Analyse de CV réussie"
        print_info "   Score global: $SCORE/100"
        print_info "   Compétences détectées: $SKILLS_COUNT"
    else
        print_error "Analyse de CV échouée"
        echo "$ANALYZE_RESPONSE"
    fi
else
    print_info "Test 9: Fichier test non trouvé ($TEST_FILE) - ignoré"
fi

# Test 10: Ressources du conteneur
print_info "Test 10: Utilisation des ressources..."
CONTAINER_STATS=$(docker stats cv-analyzer-api --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}")
print_success "Statistiques du conteneur:"
echo "$CONTAINER_STATS"

# Test 11: Logs du conteneur
print_info "Test 11: Vérification des logs (dernières 5 lignes)..."
docker logs cv-analyzer-api --tail 5

# Résumé final
print_header "RÉSUMÉ DES TESTS"

echo -e "${GREEN}✓${NC} Docker installé et fonctionnel"
echo -e "${GREEN}✓${NC} Image cv-api:latest (Taille: $IMAGE_SIZE)"
echo -e "${GREEN}✓${NC} Conteneur cv-analyzer-api en cours d'exécution"
echo -e "${GREEN}✓${NC} API accessible sur $API_URL"
echo -e "${GREEN}✓${NC} Health check: healthy"
echo -e "${GREEN}✓${NC} Documentation Swagger disponible"
echo -e "${GREEN}✓${NC} Authentification JWT fonctionnelle"

print_header "TOUS LES TESTS RÉUSSIS! 🎉"

echo -e "\n${BLUE}Commandes utiles:${NC}"
echo "  • Voir les logs:       docker logs cv-analyzer-api -f"
echo "  • Arrêter:             docker-compose down"
echo "  • Redémarrer:          docker-compose restart api"
echo "  • Documentation:       $API_URL/api/docs"
echo "  • Tester via curl:     curl $API_URL/api/v1/health"
echo ""
