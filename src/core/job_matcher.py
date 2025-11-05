"""
Job Matcher Module
Matches candidates with relevant job opportunities based on skills, experience, and regional preferences.
Includes dynamic job search from real job boards.
"""

import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from ..config import Config
from ..utils.helpers import calculate_similarity
from .job_scraper import JobScraper


class JobMatcher:
    """
    Intelligent job matching system with regional awareness and dynamic job search
    """
    
    def __init__(self):
        self.config = Config()
        self.job_database = self._load_sample_jobs()
        self.scraper = JobScraper()
    
    def search_real_jobs(
        self,
        candidate_profile: Dict[str, Any],
        region: str = "Global",
        use_dynamic_search: bool = True,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for real job opportunities dynamically
        
        Args:
            candidate_profile: Candidate's profile with skills and experience
            region: Target region for job search
            use_dynamic_search: Whether to search real job boards
            max_results: Maximum number of results
            
        Returns:
            List of real job opportunities with links
        """
        if not use_dynamic_search:
            # Use sample database
            return self.match_jobs(candidate_profile, region, max_results)
        
        # Extract search keywords from profile
        keywords = []
        
        # Add top technical skills
        if candidate_profile.get('technical_skills'):
            keywords.extend(candidate_profile['technical_skills'][:5])
        
        # Add job title if available
        if candidate_profile.get('job_title'):
            keywords.insert(0, candidate_profile['job_title'])
        
        # Perform dynamic search
        try:
            real_jobs = self.scraper.search_regional_jobs(
                keywords=keywords,
                region=region,
                max_results=max_results
            )
            
            if real_jobs:
                # Calculate match scores for real jobs
                scored_jobs = []
                for job in real_jobs:
                    match_score = self._calculate_real_job_match(job, candidate_profile)
                    job['match_percentage'] = match_score
                    job['match_details'] = self._generate_match_details(job, candidate_profile)
                    scored_jobs.append(job)
                
                # Sort by match score
                scored_jobs.sort(key=lambda x: x['match_percentage'], reverse=True)
                return scored_jobs
            
            else:
                # Fallback to search URLs
                fallback_jobs = self.scraper.get_fallback_jobs(keywords, region)
                # Add default match scores for fallback jobs
                for job in fallback_jobs:
                    job['match_percentage'] = 50  # Default score for search links
                    job['match_details'] = {
                        'required_skills_matched': 'N/A',
                        'required_skills_total': 'N/A',
                        'missing_skills': [],
                        'experience_match': 'N/A'
                    }
                return fallback_jobs
                
        except Exception as e:
            print(f"Dynamic search error: {e}")
            # Fallback to search URLs
            fallback_jobs = self.scraper.get_fallback_jobs(
                keywords=keywords,
                region=region
            )
            # Add default match scores for fallback jobs
            for job in fallback_jobs:
                job['match_percentage'] = 50  # Default score for search links
                job['match_details'] = {
                    'required_skills_matched': 'N/A',
                    'required_skills_total': 'N/A',
                    'missing_skills': [],
                    'experience_match': 'N/A'
                }
            return fallback_jobs
    
    def _calculate_real_job_match(
        self,
        job: Dict[str, Any],
        candidate_profile: Dict[str, Any]
    ) -> int:
        """
        Calculate match percentage for a real job listing
        """
        score = 0
        max_score = 100
        
        job_text = f"{job['title']} {job.get('description', '')}".lower()
        
        # Skill matching (60 points)
        candidate_skills = [
            s.lower() for s in 
            candidate_profile.get('technical_skills', []) + 
            candidate_profile.get('soft_skills', [])
        ]
        
        skill_matches = sum(1 for skill in candidate_skills if skill in job_text)
        total_skills = len(candidate_skills) if candidate_skills else 1
        skill_score = min(60, (skill_matches / total_skills) * 60)
        score += skill_score
        
        # Experience level matching (30 points)
        candidate_exp = candidate_profile.get('experience_years', 0)
        job_title_lower = job['title'].lower()
        
        if candidate_exp >= 7 and any(word in job_title_lower for word in ['senior', 'lead', 'principal']):
            score += 30
        elif 3 <= candidate_exp < 7 and any(word in job_title_lower for word in ['mid', 'intermediate']):
            score += 30
        elif candidate_exp < 3 and any(word in job_title_lower for word in ['junior', 'entry', 'graduate']):
            score += 30
        else:
            score += 15  # Partial match
        
        # Location/Remote (10 points)
        if 'remote' in job_text or 'work from home' in job_text:
            score += 10
        else:
            score += 5
        
        return min(max_score, int(score))
    
    def _generate_match_details(
        self,
        job: Dict[str, Any],
        candidate_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate detailed match information for a real job
        """
        job_text = f"{job['title']} {job.get('description', '')}".lower()
        
        candidate_skills = [
            s.lower() for s in 
            candidate_profile.get('technical_skills', []) + 
            candidate_profile.get('soft_skills', [])
        ]
        
        matched_skills = [s for s in candidate_skills if s in job_text]
        
        return {
            'matched_skills': matched_skills,
            'total_candidate_skills': len(candidate_skills),
            'match_type': 'dynamic_search',
            'source': job.get('source', 'Unknown')
        }
    
    def _load_sample_jobs(self) -> List[Dict[str, Any]]:
        """Load sample job postings for different regions"""
        return [
            # MENA Region
            {
                "id": "JOB001",
                "title": "Senior Software Engineer",
                "company": "TechCorp MENA",
                "location": "Dubai, UAE",
                "region": "MENA",
                "industry": "Technology",
                "level": "Senior",
                "required_skills": [
                    "Python", "Django", "React", "PostgreSQL", "AWS", "Docker"
                ],
                "preferred_skills": ["Kubernetes", "Redis", "CI/CD"],
                "experience_years": 5,
                "description": "Leading technology company seeking experienced software engineer to build scalable applications.",
                "salary_range": "$80,000 - $120,000",
                "remote": True
            },
            {
                "id": "JOB002",
                "title": "Data Scientist",
                "company": "Analytics Middle East",
                "location": "Riyadh, Saudi Arabia",
                "region": "MENA",
                "industry": "Technology",
                "level": "Mid-Level",
                "required_skills": [
                    "Python", "Machine Learning", "Pandas", "Scikit-learn", "SQL"
                ],
                "preferred_skills": ["Deep Learning", "TensorFlow", "Big Data"],
                "experience_years": 3,
                "description": "Join our data science team to drive insights from large datasets.",
                "salary_range": "$60,000 - $90,000",
                "remote": False
            },
            {
                "id": "JOB003",
                "title": "Frontend Developer",
                "company": "Digital Solutions Egypt",
                "location": "Cairo, Egypt",
                "region": "North Africa",
                "industry": "Technology",
                "level": "Junior",
                "required_skills": ["JavaScript", "React", "HTML", "CSS", "Git"],
                "preferred_skills": ["TypeScript", "Redux", "Testing"],
                "experience_years": 2,
                "description": "Growing startup looking for passionate frontend developers.",
                "salary_range": "$30,000 - $50,000",
                "remote": True
            },
            # Sub-Saharan Africa
            {
                "id": "JOB004",
                "title": "Mobile Developer",
                "company": "Mobile Money Africa",
                "location": "Nairobi, Kenya",
                "region": "Sub-Saharan Africa",
                "industry": "Fintech",
                "level": "Mid-Level",
                "required_skills": [
                    "Java", "Kotlin", "Android", "Mobile Development", "REST API"
                ],
                "preferred_skills": ["Flutter", "Firebase", "Agile"],
                "experience_years": 3,
                "description": "Build next-generation mobile banking solutions for Africa.",
                "salary_range": "$40,000 - $70,000",
                "remote": False
            },
            {
                "id": "JOB005",
                "title": "DevOps Engineer",
                "company": "Cloud Services SA",
                "location": "Cape Town, South Africa",
                "region": "Sub-Saharan Africa",
                "industry": "Technology",
                "level": "Senior",
                "required_skills": [
                    "AWS", "Docker", "Kubernetes", "CI/CD", "Linux", "Python"
                ],
                "preferred_skills": ["Terraform", "Ansible", "Monitoring"],
                "experience_years": 5,
                "description": "Scale cloud infrastructure for enterprise clients.",
                "salary_range": "$70,000 - $100,000",
                "remote": True
            },
            {
                "id": "JOB006",
                "title": "Full Stack Developer",
                "company": "EdTech Africa",
                "location": "Lagos, Nigeria",
                "region": "Sub-Saharan Africa",
                "industry": "Education",
                "level": "Mid-Level",
                "required_skills": [
                    "JavaScript", "Node.js", "React", "MongoDB", "Express.js"
                ],
                "preferred_skills": ["TypeScript", "AWS", "Testing"],
                "experience_years": 3,
                "description": "Help build educational platforms for African students.",
                "salary_range": "$35,000 - $60,000",
                "remote": True
            },
            # Additional roles
            {
                "id": "JOB007",
                "title": "AI/ML Engineer",
                "company": "AI Innovations MENA",
                "location": "Abu Dhabi, UAE",
                "region": "MENA",
                "industry": "Technology",
                "level": "Senior",
                "required_skills": [
                    "Python", "Machine Learning", "Deep Learning", "TensorFlow",
                    "PyTorch", "NLP"
                ],
                "preferred_skills": ["Computer Vision", "MLOps", "Kubernetes"],
                "experience_years": 5,
                "description": "Develop cutting-edge AI solutions for government and enterprise.",
                "salary_range": "$90,000 - $140,000",
                "remote": False
            },
            {
                "id": "JOB008",
                "title": "Backend Developer",
                "company": "E-Commerce Morocco",
                "location": "Casablanca, Morocco",
                "region": "North Africa",
                "industry": "Retail",
                "level": "Junior",
                "required_skills": [
                    "Python", "Django", "PostgreSQL", "REST API", "Git"
                ],
                "preferred_skills": ["Redis", "Docker", "Celery"],
                "experience_years": 1,
                "description": "Join growing e-commerce platform serving North Africa.",
                "salary_range": "$25,000 - $45,000",
                "remote": False
            },
            {
                "id": "JOB009",
                "title": "Project Manager - IT",
                "company": "Consulting Group Tunisia",
                "location": "Tunis, Tunisia",
                "region": "North Africa",
                "industry": "Consulting",
                "level": "Senior",
                "required_skills": [
                    "Project Management", "Agile", "Scrum", "Leadership",
                    "Communication", "Stakeholder Management"
                ],
                "preferred_skills": ["PMP", "Technical Background", "French"],
                "experience_years": 7,
                "description": "Lead digital transformation projects for clients across Africa.",
                "salary_range": "$50,000 - $80,000",
                "remote": False
            },
            {
                "id": "JOB010",
                "title": "Cloud Architect",
                "company": "Enterprise Solutions MENA",
                "location": "Doha, Qatar",
                "region": "MENA",
                "industry": "Technology",
                "level": "Lead",
                "required_skills": [
                    "AWS", "Azure", "Cloud Architecture", "Microservices",
                    "Security", "DevOps"
                ],
                "preferred_skills": ["Kubernetes", "Terraform", "Multi-cloud"],
                "experience_years": 8,
                "description": "Design enterprise cloud solutions for major corporations.",
                "salary_range": "$110,000 - $160,000",
                "remote": False
            }
        ]
    
    def match_jobs(
        self,
        candidate_profile: Dict[str, Any],
        region: str = None,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Match jobs based on candidate profile
        
        Args:
            candidate_profile: Candidate information from resume analysis
            region: Preferred region (optional)
            top_n: Number of top matches to return
            
        Returns:
            List of matched jobs with scores
        """
        candidate_skills = (
            candidate_profile.get("technical_skills", []) +
            candidate_profile.get("soft_skills", [])
        )
        candidate_experience = candidate_profile.get("experience_years", 0)
        
        matched_jobs = []
        
        for job in self.job_database:
            # Filter by region if specified
            if region and region != "Global" and job["region"] != region:
                continue
            
            # Calculate match score
            match_score = self._calculate_match_score(
                candidate_skills,
                candidate_experience,
                job
            )
            
            if match_score["total_score"] >= self.config.MATCH_THRESHOLD:
                matched_jobs.append({
                    **job,
                    "match_score": match_score["total_score"],
                    "match_details": match_score,
                    "match_percentage": int(match_score["total_score"] * 100)
                })
        
        # Sort by match score
        matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matched_jobs[:top_n]
    
    def _calculate_match_score(
        self,
        candidate_skills: List[str],
        candidate_experience: float,
        job: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate comprehensive match score"""
        
        # Skill matching (60% weight)
        required_skills = job["required_skills"]
        preferred_skills = job.get("preferred_skills", [])
        
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        
        # Required skills match
        required_matches = sum(
            1 for skill in required_skills
            if skill.lower() in candidate_skills_lower
        )
        required_score = required_matches / len(required_skills) if required_skills else 0
        
        # Preferred skills match
        preferred_matches = sum(
            1 for skill in preferred_skills
            if skill.lower() in candidate_skills_lower
        )
        preferred_score = (
            preferred_matches / len(preferred_skills) if preferred_skills else 0
        )
        
        skill_score = (required_score * 0.8) + (preferred_score * 0.2)
        
        # Experience matching (30% weight)
        required_experience = job.get("experience_years", 0)
        experience_diff = abs(candidate_experience - required_experience)
        
        if experience_diff == 0:
            experience_score = 1.0
        elif experience_diff <= 1:
            experience_score = 0.9
        elif experience_diff <= 2:
            experience_score = 0.7
        elif experience_diff <= 3:
            experience_score = 0.5
        else:
            experience_score = 0.3
        
        # Level appropriateness (10% weight)
        level_score = 0.8  # Default moderate match
        
        # Calculate total score
        total_score = (
            skill_score * 0.6 +
            experience_score * 0.3 +
            level_score * 0.1
        )
        
        return {
            "total_score": round(total_score, 2),
            "skill_score": round(skill_score, 2),
            "experience_score": round(experience_score, 2),
            "level_score": round(level_score, 2),
            "required_skills_matched": required_matches,
            "required_skills_total": len(required_skills),
            "preferred_skills_matched": preferred_matches,
            "missing_skills": [
                skill for skill in required_skills
                if skill.lower() not in candidate_skills_lower
            ]
        }
    
    def get_regional_insights(self, region: str) -> Dict[str, Any]:
        """Get insights about job market in specific region"""
        regional_jobs = [j for j in self.job_database if j["region"] == region]
        
        if not regional_jobs:
            return {"error": "No data available for this region"}
        
        # Aggregate insights
        industries = {}
        top_skills = {}
        avg_experience = 0
        
        for job in regional_jobs:
            # Count industries
            industry = job["industry"]
            industries[industry] = industries.get(industry, 0) + 1
            
            # Count skills
            for skill in job["required_skills"] + job.get("preferred_skills", []):
                top_skills[skill] = top_skills.get(skill, 0) + 1
            
            # Sum experience
            avg_experience += job.get("experience_years", 0)
        
        avg_experience = avg_experience / len(regional_jobs) if regional_jobs else 0
        
        # Sort and get top items
        top_industries = sorted(industries.items(), key=lambda x: x[1], reverse=True)
        top_skills_sorted = sorted(top_skills.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "region": region,
            "total_jobs": len(regional_jobs),
            "top_industries": dict(top_industries),
            "top_skills": dict(top_skills_sorted),
            "avg_experience_required": round(avg_experience, 1),
            "regional_skills": self.config.REGIONAL_SKILLS.get(region, [])
        }
    
    def recommend_skill_development(
        self,
        current_skills: List[str],
        target_region: str = None
    ) -> List[Dict[str, Any]]:
        """Recommend skills to develop for better job matches"""
        
        # Get all skills from job database
        all_job_skills = {}
        
        for job in self.job_database:
            if target_region and job["region"] != target_region:
                continue
            
            for skill in job["required_skills"]:
                all_job_skills[skill] = all_job_skills.get(skill, 0) + 2  # Required skills weighted more
            
            for skill in job.get("preferred_skills", []):
                all_job_skills[skill] = all_job_skills.get(skill, 0) + 1
        
        # Find skills not in current profile
        current_skills_lower = [s.lower() for s in current_skills]
        missing_skills = [
            (skill, count) for skill, count in all_job_skills.items()
            if skill.lower() not in current_skills_lower
        ]
        
        # Sort by demand
        missing_skills.sort(key=lambda x: x[1], reverse=True)
        
        # Format recommendations
        recommendations = []
        for skill, demand in missing_skills[:10]:
            recommendations.append({
                "skill": skill,
                "demand_score": demand,
                "priority": "High" if demand > 5 else "Medium" if demand > 2 else "Low",
                "reason": f"Required/preferred in {demand} job postings"
            })
        
        return recommendations
