"""
Job matching and search endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class JobSearchRequest(BaseModel):
    """Job search request model"""
    keywords: List[str]
    region: Optional[str] = "Global"
    experience_level: Optional[str] = None
    max_results: int = 20


class JobMatch(BaseModel):
    """Job match model"""
    id: Optional[str] = None
    title: str
    company: str
    location: str
    url: str
    match_percentage: int
    source: str
    description: Optional[str] = None


class JobSearchResponse(BaseModel):
    """Job search response model"""
    total: int
    jobs: List[JobMatch]
    search_method: str


@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest):
    """
    Search for jobs matching criteria
    Uses vector-based semantic search if available
    """
    from ...core.job_scraper import JobScraper
    from ...security.validators import sanitize_input
    
    try:
        # Sanitize keywords
        keywords = [sanitize_input(kw, max_length=100) for kw in request.keywords]
        keywords = [kw for kw in keywords if kw]  # Remove empty
        
        if not keywords:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one valid keyword required"
            )
        
        # Search jobs
        scraper = JobScraper()
        jobs = scraper.search_jobs(
            keywords=keywords,
            location=request.region,
            experience_level=request.experience_level,
            max_results=request.max_results
        )
        
        # Convert to response format
        job_matches = [
            JobMatch(
                id=job.get('id'),
                title=job['title'],
                company=job['company'],
                location=job['location'],
                url=job['url'],
                match_percentage=job.get('match_percentage', 50),
                source=job['source'],
                description=job.get('description')
            )
            for job in jobs
        ]
        
        return JobSearchResponse(
            total=len(job_matches),
            jobs=job_matches,
            search_method="scraping"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


class CandidateProfile(BaseModel):
    """Candidate profile for matching"""
    technical_skills: List[str]
    soft_skills: List[str]
    experience_years: float
    job_title: Optional[str] = None


class MatchRequest(BaseModel):
    """Job matching request"""
    candidate: CandidateProfile
    region: Optional[str] = "Global"
    top_k: int = 10


@router.post("/match", response_model=JobSearchResponse)
async def match_jobs(request: MatchRequest):
    """
    Match candidate profile to jobs using semantic similarity
    Falls back to keyword matching if vector search unavailable
    """
    try:
        # Try vector-based matching first
        try:
            from ...nlp.vector_matcher import VectorJobMatcher
            from ...core.job_matcher import JobMatcher
            
            # Get job database
            job_matcher = JobMatcher()
            jobs = job_matcher._load_sample_jobs()
            
            # Build vector index
            vector_matcher = VectorJobMatcher()
            vector_matcher.build_index(jobs)
            
            # Match
            candidate_dict = request.candidate.dict()
            matched_jobs = vector_matcher.match_jobs(
                candidate=candidate_dict,
                top_k=request.top_k,
                region_filter=request.region
            )
            
            search_method = "vector_similarity"
            
        except ImportError:
            logger.warning("Vector matching not available, using fallback")
            # Fallback to keyword matching
            from ...core.job_matcher import JobMatcher
            
            job_matcher = JobMatcher()
            candidate_dict = request.candidate.dict()
            matched_jobs = job_matcher.match_jobs(
                candidate_profile=candidate_dict,
                region=request.region,
                top_n=request.top_k
            )
            
            search_method = "keyword_matching"
        
        # Convert to response format
        job_matches = [
            JobMatch(
                id=job.get('id'),
                title=job['title'],
                company=job['company'],
                location=job['location'],
                url=job.get('url', '#'),
                match_percentage=job.get('match_percentage', 0),
                source=job.get('source', 'database'),
                description=job.get('description')
            )
            for job in matched_jobs
        ]
        
        return JobSearchResponse(
            total=len(job_matches),
            jobs=job_matches,
            search_method=search_method
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job matching failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Matching failed: {str(e)}"
        )


@router.get("/regions")
async def get_regions():
    """
    Get available job regions
    """
    from ...config import Config
    return {"regions": Config.REGIONS}


@router.get("/industries")
async def get_industries():
    """
    Get available industries
    """
    from ...config import Config
    return {"industries": Config.INDUSTRIES}
