#!/bin/bash

# 🔐 Script de génération de clés de sécurité pour Railway
# Génère des clés sécurisées pour les variables d'environnement

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     🔐 GÉNÉRATION DES CLÉS DE SÉCURITÉ                        ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Fonction pour générer une clé
generate_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))"
}

echo "📋 Variables d'environnement pour Railway:"
echo "════════════════════════════════════════════════════════════════"
echo ""

SECRET_KEY=$(generate_key)
JWT_SECRET=$(generate_key)
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

echo "# Copier-coller ces valeurs dans Railway > Variables"
echo ""
echo "SECRET_KEY=$SECRET_KEY"
echo "JWT_SECRET=$JWT_SECRET"
echo "ENCRYPTION_KEY=$ENCRYPTION_KEY"
echo "ALLOWED_ORIGINS=*"
echo "LOG_LEVEL=info"
echo "DEBUG=False"
echo "APP_ENV=production"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✅ Clés générées avec succès!"
echo ""
echo "📝 Instructions:"
echo "   1. Copier les valeurs ci-dessus"
echo "   2. Aller sur Railway Dashboard → Variables"
echo "   3. Coller chaque variable"
echo "   4. Sauvegarder"
echo ""
echo "⚠️  IMPORTANT: Ne partagez JAMAIS ces clés publiquement!"
echo ""

# Sauvegarder dans un fichier (à ne pas commit!)
cat > .env.railway << EOF
# Variables d'environnement Railway - NE PAS COMMIT!
SECRET_KEY=$SECRET_KEY
JWT_SECRET=$JWT_SECRET
ENCRYPTION_KEY=$ENCRYPTION_KEY
ALLOWED_ORIGINS=*
LOG_LEVEL=info
DEBUG=False
APP_ENV=production
EOF

echo "💾 Clés sauvegardées dans: .env.railway (local uniquement)"
echo ""
