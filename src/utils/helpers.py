"""
Helper Utilities
Common functions used across the application
"""

import re
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import json


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Raw text string
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-@]', '', text)
    return text.strip()


def extract_email(text: str) -> Optional[str]:
    """Extract email address from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text"""
    phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple similarity between two texts using word overlap
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0 and 1
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


def hash_text(text: str) -> str:
    """Create hash of text for caching"""
    return hashlib.md5(text.encode()).hexdigest()


def format_score(score: float, max_score: int = 100) -> int:
    """Format a float score to percentage"""
    return min(int(score * max_score), max_score)


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + "..."


def save_json(data: Dict[Any, Any], filepath: Path) -> None:
    """Save data as JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: Path) -> Dict[Any, Any]:
    """Load data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Check if file has allowed extension"""
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)


def get_file_size_mb(file_bytes: bytes) -> float:
    """Get file size in MB"""
    return len(file_bytes) / (1024 * 1024)


def extract_skills_from_text(text: str, skill_list: List[str]) -> List[str]:
    """
    Extract skills from text based on predefined skill list
    
    Args:
        text: Text to search
        skill_list: List of skills to look for
        
    Returns:
        List of found skills
    """
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_list:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills


def calculate_ats_score(text: str, keywords: List[str]) -> Dict[str, Any]:
    """
    Calculate ATS (Applicant Tracking System) compatibility score
    
    Args:
        text: Resume text
        keywords: List of important keywords
        
    Returns:
        Dictionary with score and analysis
    """
    text_lower = text.lower()
    found_keywords = []
    missing_keywords = []
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    
    score = len(found_keywords) / len(keywords) if keywords else 0
    
    return {
        "score": score,
        "percentage": format_score(score),
        "found_keywords": found_keywords,
        "missing_keywords": missing_keywords,
        "total_keywords": len(keywords)
    }
