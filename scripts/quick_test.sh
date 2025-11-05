#!/bin/bash

# Script de test rapide pour l'analyseur de CV
# Usage: ./quick_test.sh [fichier_cv]

set -e

echo "🧪 Test Rapide de l'Analyseur de CV"
echo "===================================="
echo ""

# Vérifier si un fichier est fourni
if [ -z "$1" ]; then
    echo "📄 Utilisation du CV de test par défaut..."
    CV_FILE="/workspaces/cv-ai-/temp/test_cv_sample.txt"
else
    CV_FILE="$1"
    echo "📄 Analyse du fichier: $CV_FILE"
fi

# Vérifier que le fichier existe
if [ ! -f "$CV_FILE" ]; then
    echo "❌ Erreur: Le fichier $CV_FILE n'existe pas"
    exit 1
fi

echo ""
echo "🔍 Vérification des services..."

# Vérifier FastAPI
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "✅ FastAPI: Opérationnel"
else
    echo "❌ FastAPI: Non accessible sur le port 8000"
    echo "   Démarrez-le avec: cd /workspaces/cv-ai- && ./venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000"
    exit 1
fi

# Vérifier Node Proxy
if curl -s http://localhost:4000/healthz > /dev/null 2>&1; then
    echo "✅ Node Proxy: Opérationnel"
else
    echo "❌ Node Proxy: Non accessible sur le port 4000"
    echo "   Démarrez-le avec: cd /workspaces/cv-ai-/examples/integration/node-proxy && node server.js"
    exit 1
fi

echo ""
echo "🚀 Envoi du CV pour analyse..."
echo ""

# Analyser le CV
RESPONSE=$(curl -s -X POST http://localhost:4000/api/resume/analyze -F "file=@$CV_FILE")

# Vérifier si la réponse contient une erreur
if echo "$RESPONSE" | grep -q "error"; then
    echo "❌ Erreur lors de l'analyse:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    exit 1
fi

# Afficher les résultats
echo "✅ Analyse réussie!"
echo ""
echo "📊 RÉSULTATS:"
echo "============="
echo ""

# Parser et afficher les scores
OVERALL_SCORE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['overall_score'])" 2>/dev/null || echo "N/A")
ATS_SCORE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['ats_score'])" 2>/dev/null || echo "N/A")
EXPERIENCE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['experience_years'])" 2>/dev/null || echo "N/A")

echo "🎯 Score Global: $OVERALL_SCORE/100"
echo "🎯 Score ATS: $ATS_SCORE/100"
echo "💼 Expérience: $EXPERIENCE ans"
echo ""

# Compétences techniques
echo "💻 Compétences Techniques:"
echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
skills = data.get('technical_skills', [])
print(f'   Total: {len(skills)}')
if skills:
    print('   -', ', '.join(skills[:10]))
    if len(skills) > 10:
        print(f'   ... et {len(skills) - 10} autres')
" 2>/dev/null || echo "   N/A"

echo ""

# Soft skills
echo "🤝 Soft Skills:"
echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
skills = data.get('soft_skills', [])
print(f'   Total: {len(skills)}')
if skills:
    print('   -', ', '.join(skills))
" 2>/dev/null || echo "   N/A"

echo ""

# Points forts
echo "✨ Points Forts:"
echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
strengths = data.get('strengths', [])
for i, strength in enumerate(strengths[:3], 1):
    print(f'   {i}. {strength}')
if len(strengths) > 3:
    print(f'   ... et {len(strengths) - 3} autres')
" 2>/dev/null || echo "   N/A"

echo ""

# Suggestions
echo "💡 Suggestions (top 3):"
echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
suggestions = data.get('suggestions', [])
for i, suggestion in enumerate(suggestions[:3], 1):
    print(f'   {i}. {suggestion}')
" 2>/dev/null || echo "   N/A"

echo ""
echo "========================================"
echo ""
echo "📄 Pour voir la réponse JSON complète:"
echo "   curl -X POST http://localhost:4000/api/resume/analyze \\"
echo "     -F \"file=@$CV_FILE\" | python3 -m json.tool"
echo ""
echo "🌐 Pour tester l'interface web:"
echo "   1. Ouvrir http://localhost:3000"
echo "   2. Uploader votre CV"
echo "   3. Cliquer sur 'Analyser le CV'"
echo ""
echo "✅ Test terminé avec succès!"
