"""
FastAPI Backend for UtopiaHire
Provides RESTful API endpoints for resume analysis, job matching, and more
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import logging
from pathlib import Path

from .routes import resume, jobs, auth, health
from .middleware import RateLimitMiddleware, SecurityHeadersMiddleware, LoggingMiddleware
from ..config import Config

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="UtopiaHire API",
        description="AI-powered career development platform API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:8501",  # Streamlit default
            "https://utopiahire.com"  # Production
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Custom middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
    app.add_middleware(LoggingMiddleware)
    
    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(resume.router, prefix="/api/v1/resume", tags=["Resume"])
    app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        logger.info("UtopiaHire API starting up...")
        # Initialize connections, load models, etc.
        # Could load vector index, connect to database, etc.
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("UtopiaHire API shutting down...")
        # Cleanup resources
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
