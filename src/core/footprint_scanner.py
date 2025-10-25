"""
Footprint Scanner Module
Analyzes professional online presence across LinkedIn, GitHub, and StackOverflow.
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..config import Config


class FootprintScanner:
    """
    Scans and analyzes professional digital footprint
    """
    
    def __init__(self):
        self.config = Config()
    
    def analyze_footprint(
        self,
        linkedin_url: str = None,
        github_username: str = None,
        stackoverflow_url: str = None
    ) -> Dict[str, Any]:
        """
        Analyze digital footprint across platforms
        
        Args:
            linkedin_url: LinkedIn profile URL
            github_username: GitHub username
            stackoverflow_url: StackOverflow profile URL
            
        Returns:
            Comprehensive footprint analysis
        """
        results = {
            "platforms_analyzed": [],
            "overall_score": 0,
            "linkedin": None,
            "github": None,
            "stackoverflow": None,
            "recommendations": [],
            "strengths": [],
            "areas_for_improvement": [],
            "analyzed_at": datetime.now().isoformat()
        }
        
        scores = []
        
        # Analyze LinkedIn
        if linkedin_url:
            linkedin_analysis = self._analyze_linkedin(linkedin_url)
            results["linkedin"] = linkedin_analysis
            results["platforms_analyzed"].append("LinkedIn")
            scores.append(linkedin_analysis["score"])
        
        # Analyze GitHub
        if github_username:
            github_analysis = self._analyze_github(github_username)
            results["github"] = github_analysis
            results["platforms_analyzed"].append("GitHub")
            scores.append(github_analysis["score"])
        
        # Analyze StackOverflow
        if stackoverflow_url:
            stackoverflow_analysis = self._analyze_stackoverflow(stackoverflow_url)
            results["stackoverflow"] = stackoverflow_analysis
            results["platforms_analyzed"].append("StackOverflow")
            scores.append(stackoverflow_analysis["score"])
        
        # Calculate overall score
        if scores:
            results["overall_score"] = int(sum(scores) / len(scores))
        
        # Generate comprehensive recommendations
        results["recommendations"] = self._generate_comprehensive_recommendations(results)
        
        # Identify strengths and improvements
        results["strengths"], results["areas_for_improvement"] = (
            self._analyze_strengths_weaknesses(results)
        )
        
        return results
    
    def _analyze_linkedin(self, url: str) -> Dict[str, Any]:
        """
        Analyze LinkedIn profile (demo version with URL validation)
        In production, this would use LinkedIn API
        """
        analysis = {
            "platform": "LinkedIn",
            "url": url,
            "is_valid": self._validate_linkedin_url(url),
            "score": 0,
            "insights": [],
            "recommendations": []
        }
        
        if not analysis["is_valid"]:
            analysis["recommendations"].append("Provide a valid LinkedIn profile URL")
            return analysis
        
        # Demo analysis (in production, would fetch actual data)
        analysis["insights"] = [
            {
                "category": "Profile Completeness",
                "status": "Good",
                "description": "Profile URL is valid and accessible"
            },
            {
                "category": "Professional Network",
                "status": "To be analyzed",
                "description": "Connect LinkedIn API for detailed network analysis"
            },
            {
                "category": "Content Activity",
                "status": "To be analyzed",
                "description": "Posts, articles, and engagement metrics"
            },
            {
                "category": "Endorsements",
                "status": "To be analyzed",
                "description": "Skills endorsed by connections"
            }
        ]
        
        # Score based on having a profile
        analysis["score"] = 60  # Base score for having a valid profile
        
        analysis["recommendations"] = [
            "Complete all profile sections (Summary, Experience, Education, Skills)",
            "Add a professional profile photo and banner",
            "Request endorsements from colleagues for key skills",
            "Publish articles or posts to demonstrate expertise",
            "Grow your network with industry professionals",
            "Join and participate in relevant LinkedIn groups"
        ]
        
        return analysis
    
    def _analyze_github(self, username: str) -> Dict[str, Any]:
        """
        Analyze GitHub profile (demo version)
        In production, this would use GitHub API
        """
        analysis = {
            "platform": "GitHub",
            "username": username,
            "is_valid": self._validate_github_username(username),
            "score": 0,
            "insights": [],
            "recommendations": [],
            "demo_stats": {}
        }
        
        if not analysis["is_valid"]:
            analysis["recommendations"].append("Provide a valid GitHub username")
            return analysis
        
        # Demo stats (in production, fetch from GitHub API)
        analysis["demo_stats"] = {
            "profile_url": f"https://github.com/{username}",
            "public_repos": "To be fetched via API",
            "followers": "To be fetched via API",
            "contributions": "To be fetched via API",
            "popular_languages": ["Python", "JavaScript", "TypeScript"],
            "activity_level": "Moderate"
        }
        
        analysis["insights"] = [
            {
                "category": "Repository Quality",
                "status": "To be analyzed",
                "description": "Number and quality of public repositories"
            },
            {
                "category": "Contribution Activity",
                "status": "To be analyzed",
                "description": "Commit frequency and consistency"
            },
            {
                "category": "Code Quality",
                "status": "To be analyzed",
                "description": "Documentation, testing, and best practices"
            },
            {
                "category": "Community Engagement",
                "status": "To be analyzed",
                "description": "Stars, forks, and collaboration"
            }
        ]
        
        analysis["score"] = 65  # Base score for having a profile
        
        analysis["recommendations"] = [
            "Maintain consistent contribution activity (green squares!)",
            "Create pinned repositories showcasing best work",
            "Write comprehensive README files for all projects",
            "Add proper documentation and comments to code",
            "Contribute to open-source projects in your field",
            "Use GitHub Actions for CI/CD demonstrations",
            "Include project descriptions and tags for discoverability"
        ]
        
        return analysis
    
    def _analyze_stackoverflow(self, url: str) -> Dict[str, Any]:
        """
        Analyze StackOverflow profile (demo version)
        In production, this would use StackOverflow API
        """
        analysis = {
            "platform": "StackOverflow",
            "url": url,
            "is_valid": self._validate_stackoverflow_url(url),
            "score": 0,
            "insights": [],
            "recommendations": [],
            "demo_stats": {}
        }
        
        if not analysis["is_valid"]:
            analysis["recommendations"].append("Provide a valid StackOverflow profile URL")
            return analysis
        
        # Demo stats (in production, fetch from SO API)
        analysis["demo_stats"] = {
            "reputation": "To be fetched via API",
            "badges": "To be fetched via API",
            "answers": "To be fetched via API",
            "questions": "To be fetched via API",
            "top_tags": ["python", "javascript", "sql"]
        }
        
        analysis["insights"] = [
            {
                "category": "Reputation Score",
                "status": "To be analyzed",
                "description": "Overall reputation and influence"
            },
            {
                "category": "Answer Quality",
                "status": "To be analyzed",
                "description": "Accepted answers and upvotes"
            },
            {
                "category": "Expertise Areas",
                "status": "To be analyzed",
                "description": "Top tags and technical domains"
            },
            {
                "category": "Community Involvement",
                "status": "To be analyzed",
                "description": "Questions, answers, and badges earned"
            }
        ]
        
        analysis["score"] = 55  # Base score for having a profile
        
        analysis["recommendations"] = [
            "Answer questions regularly in your area of expertise",
            "Ask well-researched questions when stuck",
            "Earn badges to demonstrate consistent contribution",
            "Build reputation through high-quality answers",
            "Focus on tags relevant to your career goals",
            "Provide code examples and explanations in answers"
        ]
        
        return analysis
    
    def _validate_linkedin_url(self, url: str) -> bool:
        """Validate LinkedIn URL format"""
        if not url:
            return False
        pattern = r'(https?://)?(www\.)?linkedin\.com/(in|profile)/[\w-]+'
        return bool(re.match(pattern, url))
    
    def _validate_github_username(self, username: str) -> bool:
        """Validate GitHub username format"""
        if not username:
            return False
        # GitHub usernames can contain alphanumeric and hyphens
        pattern = r'^[a-zA-Z0-9-]+$'
        return bool(re.match(pattern, username)) and len(username) <= 39
    
    def _validate_stackoverflow_url(self, url: str) -> bool:
        """Validate StackOverflow URL format"""
        if not url:
            return False
        pattern = r'(https?://)?(www\.)?stackoverflow\.com/users/\d+/[\w-]+'
        return bool(re.match(pattern, url))
    
    def _generate_comprehensive_recommendations(
        self,
        results: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate comprehensive recommendations across all platforms"""
        recommendations = []
        
        platforms_count = len(results["platforms_analyzed"])
        
        # Cross-platform recommendations
        if platforms_count == 0:
            recommendations.append({
                "priority": "Critical",
                "recommendation": "Create profiles on professional platforms (LinkedIn, GitHub, StackOverflow)",
                "impact": "Establishes your professional online presence"
            })
        elif platforms_count == 1:
            recommendations.append({
                "priority": "High",
                "recommendation": "Expand presence to additional platforms",
                "impact": "Increases visibility to recruiters and opportunities"
            })
        elif platforms_count == 2:
            recommendations.append({
                "priority": "Medium",
                "recommendation": "Consider adding third platform for comprehensive footprint",
                "impact": "Demonstrates well-rounded technical engagement"
            })
        else:
            recommendations.append({
                "priority": "Low",
                "recommendation": "Maintain active presence across all platforms",
                "impact": "Keeps your profile current and relevant"
            })
        
        # General best practices
        recommendations.extend([
            {
                "priority": "High",
                "recommendation": "Ensure consistency across all platforms",
                "impact": "Builds trust and professional credibility"
            },
            {
                "priority": "Medium",
                "recommendation": "Regular activity demonstrates ongoing learning",
                "impact": "Shows commitment to professional development"
            },
            {
                "priority": "Medium",
                "recommendation": "Link platforms together in profiles",
                "impact": "Creates unified professional brand"
            }
        ])
        
        return recommendations
    
    def _analyze_strengths_weaknesses(
        self,
        results: Dict[str, Any]
    ) -> tuple[List[str], List[str]]:
        """Analyze strengths and areas for improvement"""
        strengths = []
        improvements = []
        
        platforms_count = len(results["platforms_analyzed"])
        overall_score = results["overall_score"]
        
        # Strengths
        if platforms_count >= 3:
            strengths.append("Strong multi-platform presence")
        elif platforms_count >= 2:
            strengths.append("Good platform diversity")
        
        if overall_score >= 70:
            strengths.append("High overall footprint score")
        elif overall_score >= 60:
            strengths.append("Solid professional online presence")
        
        if results.get("linkedin"):
            strengths.append("LinkedIn profile established")
        
        if results.get("github"):
            strengths.append("Active GitHub presence for code portfolio")
        
        if results.get("stackoverflow"):
            strengths.append("StackOverflow profile shows community engagement")
        
        # Areas for improvement
        if platforms_count < 2:
            improvements.append("Limited platform presence - expand to more platforms")
        
        if overall_score < 60:
            improvements.append("Overall score could be improved through more activity")
        
        if not results.get("linkedin"):
            improvements.append("Missing LinkedIn profile - critical for professional networking")
        
        if not results.get("github"):
            improvements.append("Missing GitHub profile - important for technical roles")
        
        if not results.get("stackoverflow"):
            improvements.append("Consider joining StackOverflow for community engagement")
        
        # Ensure we have at least some content
        if not strengths:
            strengths.append("Beginning to build online presence")
        
        if not improvements:
            improvements.append("Continue maintaining active presence across all platforms")
        
        return strengths, improvements
    
    def generate_footprint_report(
        self,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive footprint report"""
        return {
            "summary": {
                "platforms_analyzed": len(analysis["platforms_analyzed"]),
                "overall_score": analysis["overall_score"],
                "status": self._get_status_label(analysis["overall_score"])
            },
            "platform_breakdown": {
                platform: analysis.get(platform.lower())
                for platform in analysis["platforms_analyzed"]
            },
            "key_strengths": analysis["strengths"][:5],
            "priority_improvements": analysis["areas_for_improvement"][:5],
            "action_items": [
                rec for rec in analysis["recommendations"]
                if rec["priority"] in ["Critical", "High"]
            ][:5]
        }
    
    def _get_status_label(self, score: int) -> str:
        """Get status label based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 50:
            return "Needs Improvement"
        else:
            return "Limited"
