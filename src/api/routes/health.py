"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    version: str
    services: Dict[str, bool]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns system health status
    """
    from ...security.secrets_manager import get_secrets_manager
    
    secrets_mgr = get_secrets_manager()
    health_status = secrets_mgr.health_check()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        services=health_status
    )


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint
    """
    return {"message": "pong"}
