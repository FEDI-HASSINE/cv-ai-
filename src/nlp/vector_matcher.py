"""
Vector-based Job Matching using Sentence Transformers and FAISS
Provides semantic matching instead of keyword matching
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Try to import sentence transformers and FAISS
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, using fallback matching")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("faiss not available, using simple cosine similarity")


class VectorJobMatcher:
    """
    Advanced job matching using semantic embeddings and vector similarity
    Falls back to keyword matching if libraries unavailable
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        index_path: Optional[Path] = None
    ):
        """
        Initialize vector matcher
        
        Args:
            model_name: Sentence transformer model name
            index_path: Path to save/load FAISS index
        """
        self.model_name = model_name
        self.index_path = index_path
        self.model = None
        self.index = None
        self.job_database = []
        self.job_embeddings = None
        
        # Try to load model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                logger.info(f"Loaded sentence transformer model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self.model = None
    
    def build_index(self, jobs: List[Dict[str, Any]]):
        """
        Build FAISS index from job listings
        
        Args:
            jobs: List of job dictionaries with title, description, skills
        """
        if not self.model:
            logger.warning("Model not available, skipping index build")
            return
        
        self.job_database = jobs
        
        # Generate embeddings for all jobs
        job_texts = [self._prepare_job_text(job) for job in jobs]
        
        try:
            logger.info(f"Generating embeddings for {len(jobs)} jobs...")
            self.job_embeddings = self.model.encode(
                job_texts,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            # Build FAISS index if available
            if FAISS_AVAILABLE:
                dimension = self.job_embeddings.shape[1]
                self.index = faiss.IndexFlatL2(dimension)
                self.index.add(self.job_embeddings.astype('float32'))
                logger.info(f"Built FAISS index with {len(jobs)} jobs")
                
                # Save index if path provided
                if self.index_path:
                    self._save_index()
            else:
                logger.info("Using numpy-based similarity (FAISS not available)")
                
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            self.job_embeddings = None
    
    def _prepare_job_text(self, job: Dict[str, Any]) -> str:
        """
        Prepare job text for embedding
        
        Args:
            job: Job dictionary
            
        Returns:
            Combined text representation
        """
        parts = []
        
        # Add title (weighted more)
        if 'title' in job:
            parts.append(f"Job Title: {job['title']}")
            parts.append(job['title'])  # Add twice for emphasis
        
        # Add description
        if 'description' in job:
            parts.append(f"Description: {job['description']}")
        
        # Add skills
        if 'required_skills' in job:
            skills = ', '.join(job['required_skills'])
            parts.append(f"Required Skills: {skills}")
        
        if 'preferred_skills' in job:
            skills = ', '.join(job.get('preferred_skills', []))
            if skills:
                parts.append(f"Preferred Skills: {skills}")
        
        # Add location and industry
        if 'location' in job:
            parts.append(f"Location: {job['location']}")
        
        if 'industry' in job:
            parts.append(f"Industry: {job['industry']}")
        
        return ' '.join(parts)
    
    def _prepare_candidate_text(self, candidate: Dict[str, Any]) -> str:
        """
        Prepare candidate profile for embedding
        
        Args:
            candidate: Candidate dictionary
            
        Returns:
            Combined text representation
        """
        parts = []
        
        # Add desired role if available
        if 'job_title' in candidate:
            parts.append(f"Seeking: {candidate['job_title']}")
            parts.append(candidate['job_title'])  # Emphasis
        
        # Add skills
        if 'technical_skills' in candidate:
            skills = ', '.join(candidate['technical_skills'])
            parts.append(f"Technical Skills: {skills}")
        
        if 'soft_skills' in candidate:
            skills = ', '.join(candidate['soft_skills'])
            parts.append(f"Soft Skills: {skills}")
        
        # Add experience
        if 'experience_years' in candidate:
            years = candidate['experience_years']
            parts.append(f"Experience: {years} years")
        
        # Add education/qualifications
        if 'education' in candidate:
            parts.append(f"Education: {candidate['education']}")
        
        return ' '.join(parts)
    
    def match_jobs(
        self,
        candidate: Dict[str, Any],
        top_k: int = 10,
        region_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Match candidate to jobs using semantic similarity
        
        Args:
            candidate: Candidate profile dictionary
            top_k: Number of top matches to return
            region_filter: Optional region filter
            
        Returns:
            List of matched jobs with similarity scores
        """
        if not self.model or self.job_embeddings is None:
            logger.warning("Vector matching not available, using fallback")
            return self._fallback_match(candidate, top_k, region_filter)
        
        try:
            # Generate candidate embedding
            candidate_text = self._prepare_candidate_text(candidate)
            candidate_embedding = self.model.encode([candidate_text], convert_to_numpy=True)
            
            # Filter by region if specified
            # Note: For large datasets, consider implementing filtering in FAISS search
            # or using boolean indexing to avoid array copies
            if region_filter and region_filter != "Global":
                filtered_indices = [
                    i for i, job in enumerate(self.job_database)
                    if job.get('region') == region_filter
                ]
                
                if not filtered_indices:
                    logger.warning(f"No jobs found for region: {region_filter}")
                    return []
                
                filtered_embeddings = self.job_embeddings[filtered_indices]
            else:
                filtered_indices = list(range(len(self.job_database)))
                filtered_embeddings = self.job_embeddings
            
            # Find similar jobs
            if FAISS_AVAILABLE and self.index is not None:
                # Use FAISS for fast search
                distances, indices = self.index.search(
                    candidate_embedding.astype('float32'),
                    min(top_k, len(filtered_indices))
                )
                
                # Convert distances to similarity scores (lower distance = higher similarity)
                similarities = 1 / (1 + distances[0])
                
            else:
                # Use numpy cosine similarity
                similarities = self._cosine_similarity(
                    candidate_embedding[0],
                    filtered_embeddings
                )
                
                # Get top k
                indices = np.argsort(similarities)[::-1][:top_k]
                similarities = similarities[indices]
            
            # Prepare results
            results = []
            for idx, sim in zip(indices, similarities):
                if region_filter and region_filter != "Global":
                    job_idx = filtered_indices[idx]
                else:
                    job_idx = idx
                
                job = self.job_database[job_idx].copy()
                job['match_percentage'] = int(sim * 100)
                job['semantic_score'] = float(sim)
                job['match_method'] = 'vector_similarity'
                results.append(job)
            
            return results
            
        except Exception as e:
            logger.error(f"Vector matching failed: {e}")
            return self._fallback_match(candidate, top_k, region_filter)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between vectors
        
        Args:
            vec1: First vector (1D)
            vec2: Second vector(s) (1D or 2D)
            
        Returns:
            Similarity score(s)
        """
        if vec2.ndim == 1:
            vec2 = vec2.reshape(1, -1)
        
        # Normalize
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2, axis=1, keepdims=True)
        
        # Dot product
        return np.dot(vec2_norm, vec1_norm)
    
    def _fallback_match(
        self,
        candidate: Dict[str, Any],
        top_k: int,
        region_filter: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Fallback to keyword-based matching
        
        Args:
            candidate: Candidate profile
            top_k: Number of matches
            region_filter: Region filter
            
        Returns:
            List of matched jobs
        """
        logger.info("Using keyword-based fallback matching")
        
        candidate_skills = set(
            s.lower() for s in 
            candidate.get('technical_skills', []) + candidate.get('soft_skills', [])
        )
        
        matches = []
        for job in self.job_database:
            # Apply region filter
            if region_filter and region_filter != "Global":
                if job.get('region') != region_filter:
                    continue
            
            # Calculate skill overlap
            job_skills = set(
                s.lower() for s in 
                job.get('required_skills', []) + job.get('preferred_skills', [])
            )
            
            overlap = len(candidate_skills & job_skills)
            total = len(job_skills) if job_skills else 1
            
            score = overlap / total
            
            job_copy = job.copy()
            job_copy['match_percentage'] = int(score * 100)
            job_copy['match_method'] = 'keyword_fallback'
            matches.append(job_copy)
        
        # Sort and return top k
        matches.sort(key=lambda x: x['match_percentage'], reverse=True)
        return matches[:top_k]
    
    def _save_index(self):
        """Save FAISS index and job database to disk"""
        if not self.index_path or not FAISS_AVAILABLE:
            return
        
        try:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save job database
            jobs_path = self.index_path.with_suffix('.jobs.json')
            with open(jobs_path, 'w') as f:
                json.dump(self.job_database, f, indent=2)
            
            logger.info(f"Saved index to {self.index_path}")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def _load_index(self):
        """Load FAISS index and job database from disk"""
        if not self.index_path or not self.index_path.exists():
            return False
        
        try:
            # Load FAISS index
            if FAISS_AVAILABLE:
                self.index = faiss.read_index(str(self.index_path))
            
            # Load job database
            jobs_path = self.index_path.with_suffix('.jobs.json')
            if jobs_path.exists():
                with open(jobs_path, 'r') as f:
                    self.job_database = json.load(f)
            
            logger.info(f"Loaded index from {self.index_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False


def build_job_index(
    jobs: List[Dict[str, Any]],
    index_path: Optional[Path] = None,
    model_name: str = "all-MiniLM-L6-v2"
) -> VectorJobMatcher:
    """
    Build and return a job matching index
    
    Args:
        jobs: List of job dictionaries
        index_path: Optional path to save index
        model_name: Sentence transformer model
        
    Returns:
        Initialized VectorJobMatcher
    """
    matcher = VectorJobMatcher(model_name=model_name, index_path=index_path)
    matcher.build_index(jobs)
    return matcher
