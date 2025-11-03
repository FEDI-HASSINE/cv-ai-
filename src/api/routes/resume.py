"""
Resume analysis endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import tempfile

from .auth import get_current_user_from_token

logger = logging.getLogger(__name__)

router = APIRouter()


class ResumeAnalysisResponse(BaseModel):
    """Resume analysis response model"""
    overall_score: int
    ats_score: int
    technical_skills: List[str]
    soft_skills: List[str]
    experience_years: float
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]


@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user_from_token)  # ENABLED: Require authentication
):
    """
    Analyze uploaded resume
    Returns comprehensive analysis with scores and suggestions
    Requires authentication to prevent abuse
    """
    from ...security.validators import InputValidator
    from ...security.audit_logger import get_audit_logger
    from ...utils.file_parser import parse_resume_file
    from ...core.resume_analyzer import ResumeAnalyzer
    
    # Validate file
    validator = InputValidator()
    
    if not validator.validate_file_extension(file.filename, ['.pdf', '.docx', '.doc', '.txt']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: PDF, DOCX, DOC, TXT"
        )
    
    # Sanitize filename
    safe_filename = validator.sanitize_filename(file.filename)
    
    # Get user ID from token
    user_id = current_user.get('sub', 'unknown')
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate size
        if not validator.validate_file_size(len(content), max_size_mb=10):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit"
            )
        
        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(safe_filename).suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Parse resume
            text = parse_resume_file(tmp_path)
            
            if not text:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not extract text from file"
                )
            
            # Analyze
            analyzer = ResumeAnalyzer()
            analysis = analyzer.analyze(text)
            
            # Audit log
            get_audit_logger().log_file_upload(
                user_id=user_id,
                filename=safe_filename,
                file_size=len(content),
                success=True
            )
            
            return ResumeAnalysisResponse(
                overall_score=analysis.get('overall_score', 0),
                ats_score=analysis.get('ats_score', 0),
                technical_skills=analysis.get('technical_skills', []),
                soft_skills=analysis.get('soft_skills', []),
                experience_years=analysis.get('experience_years', 0),
                strengths=analysis.get('strengths', []),
                weaknesses=analysis.get('weaknesses', []),
                suggestions=analysis.get('suggestions', [])
            )
            
        finally:
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume analysis failed: {e}")
        
        get_audit_logger().log_file_upload(
            user_id=user_id,
            filename=safe_filename,
            file_size=len(content) if 'content' in locals() else 0,
            success=False
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
