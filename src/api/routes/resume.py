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


class ResumeRewriteResponse(BaseModel):
    """Resume rewrite/optimization response model"""
    weak_phrases: List[Dict[str, Any]]
    action_verbs: Dict[str, List[str]]
    quantification: List[Dict[str, Any]]
    formatting: List[str]
    content_enhancements: List[str]
    optimized_sections: Dict[str, Any]
    recommendations: List[Dict[str, str]]
    improvement_score: int


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
    
    logger.info(f"Analyzing resume: {file.filename}")
    
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
            
            logger.info(f"Analysis completed successfully for {safe_filename}")
            
            # Audit log
            get_audit_logger().log_file_upload(
                user_id=user_id,
                filename=safe_filename,
                file_size=len(content),
                success=True
            )
            
            # Ensure all required fields are present
            response_data = {
                'overall_score': analysis.get('overall_score', 0),
                'ats_score': analysis.get('ats_score', 0),
                'technical_skills': analysis.get('technical_skills', []),
                'soft_skills': analysis.get('soft_skills', []),
                'experience_years': float(analysis.get('experience_years', 0.0)),
                'strengths': analysis.get('strengths', []),
                'weaknesses': analysis.get('weaknesses', []),
                'suggestions': analysis.get('suggestions', [])
            }
            
            logger.info(f"Response data: {response_data}")
            
            return ResumeAnalysisResponse(**response_data)
            
        finally:
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume analysis failed: {e}", exc_info=True)
        
        try:
            get_audit_logger().log_file_upload(
                user_id=user_id,
                filename=safe_filename,
                file_size=len(content) if 'content' in locals() else 0,
                success=False
            )
        except:
            pass  # Don't fail if audit logging fails
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/rewrite", response_model=ResumeRewriteResponse)
async def rewrite_resume(
    file: UploadFile = File(...),
    use_ai: bool = False,
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Generate rewriting/optimization suggestions for a resume.
    - If use_ai=False (default), uses deterministic/static heuristics (fast).
    - If use_ai=True, endpoint can be extended to call LLMs (not enabled by default here).
    """
    from ...security.validators import InputValidator
    from ...security.audit_logger import get_audit_logger
    from ...utils.file_parser import parse_resume_file
    from ...core.resume_analyzer import ResumeAnalyzer
    from ...core.resume_rewriter import ResumeRewriter

    validator = InputValidator()

    if not validator.validate_file_extension(file.filename, ['.pdf', '.docx', '.doc', '.txt']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: PDF, DOCX, DOC, TXT"
        )

    safe_filename = validator.sanitize_filename(file.filename)
    user_id = current_user.get('sub', 'unknown')

    try:
        content = await file.read()

        if not validator.validate_file_size(len(content), max_size_mb=10):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit"
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(safe_filename).suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            text = parse_resume_file(tmp_path)
            if not text:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not extract text from file"
                )

            analyzer = ResumeAnalyzer()
            analysis = analyzer.analyze(text)

            rewriter = ResumeRewriter()
            # In API, keep use_static_objects=True for speed unless you wire LLMs here later
            rewrite = rewriter.rewrite(text, analysis, use_static_objects=not use_ai)

            get_audit_logger().log_file_upload(
                user_id=user_id,
                filename=safe_filename,
                file_size=len(content),
                success=True
            )

            return ResumeRewriteResponse(**rewrite)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume rewrite failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rewrite failed: {str(e)}"
        )
