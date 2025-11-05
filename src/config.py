"""
Configuration Module
Centralizes all configuration settings for the CV-AI application.
Designed for easy API integration in the future.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TEMP_DIR = BASE_DIR / "temp"
MODELS_DIR = BASE_DIR / "models"

# Create necessary directories
for directory in [DATA_DIR, TEMP_DIR, MODELS_DIR]:
    directory.mkdir(exist_ok=True)

# Application settings
class Config:
    """Main configuration class"""
    
    # Application
    APP_NAME = "UtopiaHire - AI Career Architect"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # File upload settings
    MAX_FILE_SIZE_MB = 10
    ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc", ".txt"]
    
    # NLP Settings
    SPACY_MODEL = "en_core_web_sm"  # Lightweight model for demo
    MIN_CONFIDENCE_SCORE = 0.7
    
    # Resume Analysis
    ATS_KEYWORDS = [
        "experience", "education", "skills", "projects", "certifications",
        "achievements", "languages", "technical", "professional", "summary"
    ]
    
    # Job Matching
    DEFAULT_REGION = "MENA"
    REGIONS = ["MENA", "Sub-Saharan Africa", "North Africa", "Global"]
    MATCH_THRESHOLD = 0.6
    
    # Footprint Scanner
    PLATFORMS = ["LinkedIn", "GitHub", "StackOverflow"]
    
    # API Configuration (for future use)
    API_VERSION = "v1"
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
    API_TIMEOUT = 30
    
    # OpenAI/LLM Settings (when integrated)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    MAX_TOKENS = 1500
    TEMPERATURE = 0.7
    
    # Caching
    ENABLE_CACHE = True
    CACHE_TTL = 3600  # 1 hour
    
    # Regional Job Markets (Sample data for demo)
    REGIONAL_SKILLS = {
        "MENA": [
            "Arabic", "English", "Oil & Gas", "Construction", "Finance",
            "Tourism", "Technology", "Engineering", "Healthcare"
        ],
        "Sub-Saharan Africa": [
            "Agriculture", "Mining", "Mobile Technology", "Fintech",
            "Renewable Energy", "Education", "Healthcare", "NGO"
        ],
        "North Africa": [
            "French", "Arabic", "Manufacturing", "Technology",
            "Tourism", "Agriculture", "Trade", "Finance"
        ]
    }
    
    # Industry sectors
    INDUSTRIES = [
        "Technology", "Finance", "Healthcare", "Education", "Manufacturing",
        "Retail", "Construction", "Energy", "Agriculture", "Transportation",
        "Telecommunications", "Media", "Hospitality", "Consulting", "NGO"
    ]
    
    # Job levels
    JOB_LEVELS = [
        "Entry Level", "Junior", "Mid-Level", "Senior", "Lead",
        "Manager", "Director", "Executive"
    ]

    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Returns configuration as dictionary"""
        return {
            "app_name": Config.APP_NAME,
            "version": Config.APP_VERSION,
            "regions": Config.REGIONS,
            "industries": Config.INDUSTRIES,
            "platforms": Config.PLATFORMS
        }


# Streamlit page configuration
STREAMLIT_CONFIG = {
    "page_title": "UtopiaHire - AI Career Architect",
    "page_icon": "💼",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Color scheme
COLORS = {
    "primary": "#2E86AB",
    "secondary": "#A23B72",
    "success": "#06D6A0",
    "warning": "#F18F01",
    "danger": "#C73E1D",
    "info": "#4EA8DE"
}
