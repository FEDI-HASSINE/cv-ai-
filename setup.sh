#!/bin/bash

# UtopiaHire Setup Script

echo "🚀 Setting up UtopiaHire - AI Career Architect"
echo "================================================"

# Check Python version
echo ""
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please configure it with your API keys."
fi

# Create necessary directories
echo ""
echo "📁 Creating necessary directories..."
mkdir -p data temp models

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application, run:"
echo "  source venv/bin/activate"
echo "  streamlit run app.py"
echo ""
echo "Or simply run: ./run.sh"
