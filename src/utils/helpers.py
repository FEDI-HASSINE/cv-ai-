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


def calculate_ats_score(
    text: str,
    keywords: List[Any],
    sections: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Calculate ATS (Applicant Tracking System) compatibility score (v2)
    
    Improvements over the basic version:
    - Weighted keywords support (each keyword can have an optional weight)
    - Robust word/phrase matching using word boundaries
    - Optional synonyms/variants per keyword
    - Light frequency bonus (caps at small boost)
    - Optional structural penalties if key sections are missing

    Args:
        text: Resume text
        keywords: List of keywords, either simple strings or dicts with:
                  {"term": str, "weight": float=1.0, "synonyms": List[str]=[]}
        sections: Optional list of detected section names to apply structure penalties
        
    Returns:
        Dictionary with score and analysis
    """
    text_lower = text.lower()

    # Normalize keyword spec to a list of dicts
    norm_items: List[Dict[str, Any]] = []
    # Priority weights for common resume sections/terms (if provided as plain strings)
    priority_weights = {
        "experience": 1.5,
        "education": 1.3,
        "skills": 1.3,
        "projects": 1.2,
        "certifications": 1.2,
    }

    for item in keywords:
        if isinstance(item, str):
            base = item.strip()
            if not base:
                continue
            weight = priority_weights.get(base.lower(), 1.0)
            norm_items.append({
                "term": base,
                "weight": float(weight),
                "synonyms": []
            })
        elif isinstance(item, dict):
            term = item.get("term") or item.get("keyword") or item.get("name")
            if not term:
                continue
            norm_items.append({
                "term": str(term),
                "weight": float(item.get("weight", 1.0)),
                "synonyms": list(item.get("synonyms", []))
            })

    total_weight = sum(k["weight"] for k in norm_items) or 1.0

    def _count_occurrences(needle: str) -> int:
        # Build a regex that respects word boundaries for single tokens,
        # but also works for phrases (use simple case-insensitive search with boundaries on ends).
        escaped = re.escape(needle.lower())
        # If the phrase contains spaces or non-word chars, do a simpler search
        if re.search(r"\W", needle):
            return len(re.findall(escaped, text_lower))
        # Else use word boundaries to avoid partial matches like 'css' in 'success'
        pattern = rf"(?<!\w){escaped}(?!\w)"
        return len(re.findall(pattern, text_lower))

    found_keywords: List[str] = []
    missing_keywords: List[str] = []

    base_numerator = 0.0
    bonus = 0.0

    for spec in norm_items:
        terms = [spec["term"]] + list(spec.get("synonyms", []))
        weight = spec["weight"]

        occurrences = 0
        matched_term = None
        for t in terms:
            c = _count_occurrences(t)
            if c > 0:
                occurrences += c
                matched_term = spec["term"] if matched_term is None else matched_term
        if occurrences > 0:
            # Count as found (base weight)
            base_numerator += weight
            found_keywords.append(spec["term"])  # report the base term
            # Small frequency bonus capped to 2 extra occurrences (10% of weight each)
            extra = min(max(occurrences - 1, 0), 2)
            bonus += 0.1 * weight * extra
        else:
            missing_keywords.append(spec["term"])

    # Structural penalties for missing key sections (if provided)
    penalty = 0.0
    if sections:
        required_sections = ["Experience", "Education", "Skills"]
        for req in required_sections:
            if not any(req.lower() in s.lower() for s in sections):
                penalty += 0.05 * total_weight  # 5% of total weight per missing section
        penalty = min(penalty, 0.15 * total_weight)  # cap at 15%

    # Compute final score (0..1), guarding against negatives
    raw = (base_numerator + bonus - penalty) / total_weight
    score = max(0.0, min(1.0, raw))

    return {
        "method": "v2",
        "score": score,
        "percentage": format_score(score),
        "found_keywords": found_keywords,
        "missing_keywords": missing_keywords,
        "total_keywords": len(norm_items),
        "details": {
            "total_weight": total_weight,
            "base_weight_found": base_numerator,
            "bonus": bonus,
            "penalty": penalty
        }
    }
