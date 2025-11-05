"""
NLP Module for UtopiaHire
Enhanced semantic matching using sentence transformers and vector search
"""

from .vector_matcher import VectorJobMatcher, build_job_index
from .embeddings import EmbeddingGenerator
from .skill_extractor import SkillExtractor

__all__ = [
    'VectorJobMatcher',
    'build_job_index',
    'EmbeddingGenerator',
    'SkillExtractor'
]
