"""
Resume Analyzer Module
Analyzes resumes using NLP techniques for ATS scoring, skill extraction, and improvement suggestions.
Now powered by AI for better extraction!
"""

import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from ..config import Config
from ..utils.helpers import (
    clean_text, extract_email, extract_phone, extract_urls,
    calculate_ats_score, extract_skills_from_text
)

# Import AI extractor
try:
    from .ai_resume_extractor import AIResumeExtractor
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ AI Resume Extractor not available, using fallback methods")


class ResumeAnalyzer:
    """
    Comprehensive resume analyzer with AI-powered extraction
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.config = Config()
        self.technical_skills = self._load_technical_skills()
        self.soft_skills = self._load_soft_skills()
        
        # Initialize AI extractor if available
        self.ai_extractor = None
        if AI_AVAILABLE:
            try:
                self.ai_extractor = AIResumeExtractor(openai_api_key=openai_api_key)
                print("✅ AI Resume Extractor initialized")
            except Exception as e:
                print(f"⚠️ Could not initialize AI extractor: {e}")
    
    def _load_technical_skills(self) -> List[str]:
        """Load common technical skills"""
        return [
            # Programming Languages
            "Python", "JavaScript", "Java", "C++", "C#", "Ruby", "PHP", "Swift",
            "Kotlin", "Go", "Rust", "TypeScript", "R", "MATLAB", "Scala",
            # Web Technologies
            "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Django",
            "Flask", "FastAPI", "Express.js", "Spring Boot", "ASP.NET",
            # Databases
            "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle",
            "SQLite", "Cassandra", "DynamoDB", "Firebase",
            # Cloud & DevOps
            "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "CI/CD",
            "Jenkins", "GitLab", "Terraform", "Ansible",
            # Data Science & AI
            "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
            "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
            "Data Analysis", "Big Data", "Hadoop", "Spark",
            # Tools & Others
            "Git", "Linux", "Agile", "Scrum", "REST API", "GraphQL",
            "Microservices", "Testing", "Unit Testing", "Integration Testing"
        ]
    
    def _load_soft_skills(self) -> List[str]:
        """Load common soft skills"""
        return [
            "Leadership", "Communication", "Teamwork", "Problem Solving",
            "Critical Thinking", "Time Management", "Adaptability",
            "Creativity", "Collaboration", "Project Management",
            "Analytical", "Strategic Planning", "Presentation",
            "Negotiation", "Mentoring", "Decision Making"
        ]
    
    def analyze(self, resume_text: str) -> Dict[str, Any]:
        """
        Perform comprehensive resume analysis with AI-powered extraction
        
        Args:
            resume_text: Text content of the resume
            
        Returns:
            Complete analysis results with AI-extracted data
        """
        cleaned_text = clean_text(resume_text)
        
        # Try AI extraction first
        ai_data = None
        if self.ai_extractor:
            try:
                print("🤖 Using AI-powered extraction...")
                ai_data = self.ai_extractor.extract_resume_data(resume_text)
            except Exception as e:
                print(f"⚠️ AI extraction failed, using fallback: {e}")
        
        # Extract basic information (use AI data if available)
        if ai_data:
            contact_info = {
                "email": ai_data.get("email", ""),
                "phone": ai_data.get("phone", ""),
                "linkedin": ai_data.get("linkedin", ""),
                "github": ai_data.get("github", ""),
                "name": ai_data.get("name", "Not specified"),
                "urls": []  # Add empty list for compatibility
            }
            # Add LinkedIn and GitHub to urls if they exist
            if ai_data.get("linkedin"):
                contact_info["urls"].append(ai_data.get("linkedin"))
            if ai_data.get("github"):
                contact_info["urls"].append(ai_data.get("github"))
            
            technical_skills_found = ai_data.get("technical_skills", [])
            soft_skills_found = ai_data.get("soft_skills", [])
            experience_years = ai_data.get("experience_years", 0.0)
            education_level = ai_data.get("education", [{}])[0].get("degree", "Not specified") if ai_data.get("education") else "Not specified"
        else:
            # Fallback to regex extraction
            contact_info = self._extract_contact_info(resume_text)
            technical_skills_found = extract_skills_from_text(cleaned_text, self.technical_skills)
            soft_skills_found = extract_skills_from_text(cleaned_text, self.soft_skills)
            experience_years = self._estimate_experience(cleaned_text)
            education_level = self._detect_education_level(cleaned_text)
        
        # Section detection
        sections = self._detect_sections(cleaned_text)
        
        # ATS Score (v2 with structural context)
        ats_analysis = calculate_ats_score(
            cleaned_text,
            self.config.ATS_KEYWORDS,
            sections=sections
        )
        
        # Resume strength analysis
        strengths, weaknesses = self._analyze_strengths_weaknesses(
            sections, technical_skills_found, soft_skills_found,
            contact_info, ats_analysis
        )
        
        # Overall score calculation
        overall_score = self._calculate_overall_score(
            ats_analysis["percentage"],
            len(technical_skills_found),
            len(soft_skills_found),
            len(sections),
            bool(contact_info["email"])
        )
        
        # Improvement suggestions
        suggestions = self._generate_suggestions(
            sections, weaknesses, ats_analysis["missing_keywords"]
        )
        
        return {
            "overall_score": overall_score,
            "ai_extracted": ai_data is not None,  # Flag to show if AI was used
            "ats_score": ats_analysis["percentage"],
            "contact_info": contact_info,
            "sections_found": sections,
            "technical_skills": technical_skills_found,
            "soft_skills": soft_skills_found,
            "experience_years": experience_years,
            "education_level": education_level,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "ats_analysis": ats_analysis,
            "word_count": len(cleaned_text.split()),
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information"""
        return {
            "email": extract_email(text),
            "phone": extract_phone(text),
            "urls": extract_urls(text)
        }
    
    def _detect_sections(self, text: str) -> List[str]:
        """Detect resume sections"""
        sections = []
        section_keywords = {
            "Summary": r'(summary|profile|objective|about)',
            "Experience": r'(experience|work history|employment|professional experience)',
            "Education": r'(education|academic|qualification|degree)',
            "Skills": r'(skills|technical skills|competencies|expertise)',
            "Projects": r'(projects|portfolio|work samples)',
            "Certifications": r'(certifications|certificates|licenses)',
            "Languages": r'(languages|language proficiency)',
            "Awards": r'(awards|honors|achievements|recognition)',
            "Publications": r'(publications|research|papers)',
            "Volunteer": r'(volunteer|community|social)'
        }
        
        text_lower = text.lower()
        for section, pattern in section_keywords.items():
            if re.search(pattern, text_lower):
                sections.append(section)
        
        return sections
    
    def _estimate_experience(self, text: str) -> float:
        """Enhanced experience estimation with better date detection"""
        current_year = datetime.now().year
        
        # First, look for explicit mentions (most reliable)
        exp_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r"(\d+)\+?\s*ans?\s+d['']expérience",  # French
            r'(\d+)\+?\s*years?\s+in',
        ]
        
        for pattern in exp_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                years = float(match.group(1))
                if 0 <= years <= 50:
                    return years
        
        # Look for work experience date ranges with various formats
        date_patterns = [
            # Format: 2020 - Present, 2020 - Current, etc.
            r'(20\d{2}|19\d{2})\s*[-–—]\s*(?:present|current|now|today|ongoing)',
            # Format: Jan 2020 - Dec 2023
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(20\d{2}|19\d{2})\s*[-–—]\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(20\d{2}|19\d{2})',
            # Format: Jan 2020 - Present
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(20\d{2}|19\d{2})\s*[-–—]\s*(?:present|current)',
            # Format: 2020 - 2023
            r'(20\d{2}|19\d{2})\s*[-–—]\s*(20\d{2}|19\d{2})',
            # Format: 01/2020 - 12/2023
            r'\d{1,2}/(20\d{2}|19\d{2})\s*[-–—]\s*\d{1,2}/(20\d{2}|19\d{2})',
            # Format: 01/2020 - Present
            r'\d{1,2}/(20\d{2}|19\d{2})\s*[-–—]\s*(?:present|current)',
        ]
        
        years_found = []
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract all year groups
                for group in match.groups():
                    if group and group.isdigit():
                        year = int(group)
                        if 1970 <= year <= current_year:
                            years_found.append(year)
        
        # Calculate total experience from all date ranges
        if years_found:
            earliest_year = min(years_found)
            if current_year - earliest_year <= 50 and current_year - earliest_year > 0:
                return round(current_year - earliest_year, 1)
        
        # Last resort: Look for "since YYYY"
        since_pattern = r'since\s+(20\d{2}|19\d{2})'
        matches = re.finditer(since_pattern, text, re.IGNORECASE)
        for match in matches:
            year = int(match.group(1))
            if 1970 <= year <= current_year:
                exp_years = current_year - year
                if 0 < exp_years <= 50:
                    return float(exp_years)
        
        return 0.0
    
    def _detect_education_level(self, text: str) -> str:
        """Enhanced education level detection with more patterns"""
        text_lower = text.lower()
        
        # Expanded patterns with more variations
        education_levels = [
            ("PhD / Doctorate", r'(ph\.?\s?d|doctorate|doctoral|doctor\s+of\s+philosophy)'),
            ("Master's Degree", r"(master['']?s?\s+degree|master\s+of|m\.?\s?s\.?c?|m\.?\s?a\.?|m\.?\s?b\.?\s?a\.?|mba|msc|ma\b)"),
            ("Bachelor's Degree", r"(bachelor['']?s?\s+degree|bachelor\s+of|b\.?\s?s\.?c?|b\.?\s?a\.?|b\.?\s?tech|b\.?\s?eng|bsc|ba\b|licence)"),
            ("Associate Degree", r"(associate['']?s?\s+degree|associate\s+of|a\.?\s?s\.?|a\.?\s?a\.?)"),
            ("Diploma / Certificate", r"(diploma|certificate|certification)"),
            ("High School", r"(high\s+school|secondary\s+school|baccalaur[eé]at|bac\s+\+)"),
        ]
        
        for level, pattern in education_levels:
            if re.search(pattern, text_lower):
                return level
        
        return "Not specified"
    
    def _analyze_strengths_weaknesses(
        self,
        sections: List[str],
        technical_skills: List[str],
        soft_skills: List[str],
        contact_info: Dict[str, Any],
        ats_analysis: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """Analyze resume strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        # Check strengths
        if len(sections) >= 5:
            strengths.append("Well-structured with multiple sections")
        
        if len(technical_skills) >= 8:
            strengths.append(f"Strong technical skill set ({len(technical_skills)} skills)")
        
        if len(soft_skills) >= 4:
            strengths.append(f"Good soft skills representation ({len(soft_skills)} skills)")
        
        if ats_analysis["percentage"] >= 70:
            strengths.append("High ATS compatibility score")
        
        if contact_info["email"] and contact_info["phone"]:
            strengths.append("Complete contact information")
        
        # Check weaknesses
        if len(sections) < 4:
            weaknesses.append("Missing important sections")
        
        if len(technical_skills) < 5:
            weaknesses.append("Limited technical skills listed")
        
        if not contact_info["email"]:
            weaknesses.append("Email address not found")
        
        if ats_analysis["percentage"] < 50:
            weaknesses.append("Low ATS compatibility score")
        
        if "Experience" not in sections:
            weaknesses.append("Experience section not clearly defined")
        
        if "Education" not in sections:
            weaknesses.append("Education section not clearly defined")
        
        return strengths, weaknesses
    
    def _calculate_overall_score(
        self,
        ats_score: int,
        tech_skills_count: int,
        soft_skills_count: int,
        sections_count: int,
        has_email: bool
    ) -> int:
        """Calculate overall resume score"""
        score = 0
        
        # ATS Score (40%)
        score += ats_score * 0.4
        
        # Skills (30%)
        skills_score = min(100, (tech_skills_count * 5) + (soft_skills_count * 3))
        score += skills_score * 0.3
        
        # Structure (20%)
        structure_score = min(100, sections_count * 12)
        score += structure_score * 0.2
        
        # Contact Info (10%)
        contact_score = 100 if has_email else 50
        score += contact_score * 0.1
        
        return min(100, int(score))
    
    def _generate_suggestions(
        self,
        sections: List[str],
        weaknesses: List[str],
        missing_keywords: List[str]
    ) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Section suggestions
        important_sections = ["Summary", "Experience", "Education", "Skills"]
        for section in important_sections:
            if section not in sections:
                suggestions.append(f"Add a clear '{section}' section to your resume")
        
        # Keyword suggestions
        if missing_keywords:
            top_missing = missing_keywords[:3]
            suggestions.append(
                f"Include these important keywords: {', '.join(top_missing)}"
            )
        
        # General suggestions based on weaknesses
        if "Limited technical skills listed" in weaknesses:
            suggestions.append(
                "Expand your technical skills section with relevant technologies"
            )
        
        if "Email address not found" in weaknesses:
            suggestions.append("Add your email address in the contact section")
        
        # Standard best practices
        suggestions.extend([
            "Use action verbs to describe your achievements",
            "Quantify your accomplishments with numbers and metrics",
            "Tailor your resume to match specific job descriptions",
            "Keep your resume concise (1-2 pages for most roles)"
        ])
        
        return suggestions[:8]  # Return top 8 suggestions
