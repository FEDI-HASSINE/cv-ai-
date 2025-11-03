"""
Job Description Parser
Extracts skills, requirements, and metadata from job descriptions using NLP
"""

import re
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class JobParser:
    """
    Parse job descriptions to extract structured information
    """
    
    def __init__(self):
        """Initialize job parser"""
        self.skill_patterns = self._load_skill_patterns()
        self.experience_patterns = self._load_experience_patterns()
        self.job_type_patterns = self._load_job_type_patterns()
    
    def _load_skill_patterns(self) -> Dict[str, List[str]]:
        """Load skill detection patterns"""
        return {
            'programming': [
                'python', 'java', 'javascript', 'typescript', 'c\\+\\+', 'c#', 'ruby',
                'php', 'swift', 'kotlin', 'go', 'rust', 'scala', 'r', 'matlab'
            ],
            'web': [
                'react', 'angular', 'vue', 'node\\.?js', 'django', 'flask', 'spring',
                'express', 'fastapi', 'html', 'css', 'sass', 'less', 'webpack'
            ],
            'database': [
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                'cassandra', 'dynamodb', 'oracle', 'sql server'
            ],
            'cloud': [
                'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
                'terraform', 'ansible', 'jenkins', 'ci/cd', 'devops'
            ],
            'data_science': [
                'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras',
                'scikit-learn', 'pandas', 'numpy', 'data analysis', 'statistics'
            ],
            'mobile': [
                'android', 'ios', 'react native', 'flutter', 'xamarin', 'mobile development'
            ],
            'soft_skills': [
                'communication', 'leadership', 'teamwork', 'problem solving',
                'analytical', 'critical thinking', 'agile', 'scrum'
            ]
        }
    
    def _load_experience_patterns(self) -> Dict[str, str]:
        """Load experience level patterns"""
        return {
            'entry': r'\b(entry|junior|graduate|intern|0-2\s*years?)\b',
            'mid': r'\b(mid|intermediate|2-5\s*years?|3-5\s*years?)\b',
            'senior': r'\b(senior|lead|principal|staff|5\+?\s*years?|7\+?\s*years?)\b',
            'executive': r'\b(director|vp|vice president|c-level|cto|ceo)\b'
        }
    
    def _load_job_type_patterns(self) -> Dict[str, str]:
        """Load job type patterns"""
        return {
            'full_time': r'\b(full[\s-]?time|permanent)\b',
            'part_time': r'\b(part[\s-]?time)\b',
            'contract': r'\b(contract|contractor|freelance)\b',
            'temporary': r'\b(temporary|temp)\b',
            'internship': r'\b(intern|internship)\b'
        }
    
    def parse(self, description: str) -> Dict[str, Any]:
        """
        Parse job description
        
        Args:
            description: Job description text
            
        Returns:
            Parsed information dictionary
        """
        if not description:
            return {}
        
        description_lower = description.lower()
        
        result = {
            'required_skills': self._extract_skills(description_lower, required=True),
            'preferred_skills': self._extract_skills(description_lower, required=False),
            'experience_level': self._extract_experience_level(description_lower),
            'job_type': self._extract_job_type(description_lower),
            'salary_range': self._extract_salary(description),
            'education_required': self._extract_education(description_lower)
        }
        
        return {k: v for k, v in result.items() if v}  # Remove empty values
    
    def _extract_skills(self, text: str, required: bool = True) -> List[str]:
        """
        Extract skills from text
        
        Args:
            text: Text to search (should be lowercase)
            required: Whether to look for required or preferred skills
            
        Returns:
            List of found skills
        """
        skills = []
        
        # Look for skills section
        if required:
            section_patterns = [
                r'required skills?:?(.*?)(?:preferred|nice|optional|$)',
                r'must have:?(.*?)(?:preferred|nice|optional|$)',
                r'qualifications?:?(.*?)(?:preferred|nice|optional|$)'
            ]
        else:
            section_patterns = [
                r'preferred skills?:?(.*?)(?:required|$)',
                r'nice to have:?(.*?)(?:required|$)',
                r'optional:?(.*?)(?:required|$)'
            ]
        
        # Try to find relevant section
        search_text = text
        for pattern in section_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                search_text = match.group(1)
                break
        
        # Search for skill patterns
        for category, patterns in self.skill_patterns.items():
            for pattern in patterns:
                if re.search(r'\b' + pattern + r'\b', search_text, re.IGNORECASE):
                    # Get the original case from text
                    match = re.search(r'\b' + pattern + r'\b', search_text, re.IGNORECASE)
                    if match:
                        skill = match.group(0).strip()
                        if skill and skill not in skills:
                            skills.append(skill.title())
        
        return skills
    
    def _extract_experience_level(self, text: str) -> Optional[str]:
        """
        Extract experience level from text
        
        Args:
            text: Text to search (lowercase)
            
        Returns:
            Experience level string
        """
        for level, pattern in self.experience_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return level.capitalize()
        
        return None
    
    def _extract_job_type(self, text: str) -> Optional[str]:
        """
        Extract job type from text
        
        Args:
            text: Text to search (lowercase)
            
        Returns:
            Job type string
        """
        for job_type, pattern in self.job_type_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return job_type.replace('_', ' ').title()
        
        return None
    
    def _extract_salary(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract salary information
        
        Args:
            text: Text to search
            
        Returns:
            Dictionary with salary info
        """
        # Common salary patterns
        patterns = [
            r'\$[\d,]+\s*-\s*\$[\d,]+',  # $80,000 - $120,000
            r'[\d,]+\s*-\s*[\d,]+\s*(?:USD|EUR|GBP)',  # 80,000 - 120,000 USD
            r'\$[\d,]+k\s*-\s*\$[\d,]+k',  # $80k - $120k
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                salary_str = match.group(0)
                
                # Parse range
                numbers = re.findall(r'[\d,]+', salary_str)
                if len(numbers) >= 2:
                    try:
                        min_sal = int(numbers[0].replace(',', ''))
                        max_sal = int(numbers[1].replace(',', ''))
                        
                        # Adjust for k notation
                        if 'k' in salary_str.lower():
                            min_sal *= 1000
                            max_sal *= 1000
                        
                        return {
                            'min': min_sal,
                            'max': max_sal,
                            'currency': 'USD'  # Default, could be extracted
                        }
                    except ValueError:
                        pass
        
        return None
    
    def _extract_education(self, text: str) -> Optional[List[str]]:
        """
        Extract education requirements
        
        Args:
            text: Text to search (lowercase)
            
        Returns:
            List of education requirements
        """
        education_patterns = [
            r"bachelor'?s? degree",
            r"master'?s? degree",
            r"phd",
            r"doctorate",
            r"associate'?s? degree",
            r"high school diploma",
            r"certification"
        ]
        
        found = []
        for pattern in education_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Extract the matched text with proper casing
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    found.append(match.group(0).title())
        
        return found if found else None
    
    def extract_requirements(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all requirements from job description
        
        Args:
            text: Job description
            
        Returns:
            Dictionary with categorized requirements
        """
        return {
            'technical': self._extract_skills(text.lower(), required=True),
            'experience': [self._extract_experience_level(text.lower())] if self._extract_experience_level(text.lower()) else [],
            'education': self._extract_education(text.lower()) or [],
            'soft_skills': [skill for skill in self._extract_skills(text.lower(), required=True) 
                           if any(soft in skill.lower() for soft in self.skill_patterns['soft_skills'])]
        }
