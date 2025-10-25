#!/bin/bash

# UtopiaHire Run Script

echo "🚀 Starting UtopiaHire - AI Career Architect"
echo "============================================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Check if dependencies are installed
if ! python -c "import streamlit" &> /dev/null; then
    echo "❌ Dependencies not installed. Running setup..."
    ./setup.sh
fi

# Run the application
echo ""
echo "🌐 Starting Streamlit application..."
echo "📍 Access the app at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py
