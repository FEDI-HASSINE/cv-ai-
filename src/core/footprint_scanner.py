"""
Footprint Scanner Module
Analyzes professional online presence across LinkedIn, GitHub, and StackOverflow.

Orchestrates data collection, scoring, insights generation, and report export.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..config import Config
from .collectors.github_collector import GitHubCollector
from .collectors.stackoverflow_collector import StackOverflowCollector
from .collectors.linkedin_scraper import LinkedInScraper
from .scoring_engine import ScoringEngine
from .insights_generator import InsightsGenerator
from .exporters.text_exporter import TextExporter
from .exporters.json_exporter import JSONExporter

logger = logging.getLogger(__name__)


class FootprintScanner:
    """
    Orchestrates comprehensive digital footprint analysis.
    
    Collects data from GitHub, StackOverflow, and LinkedIn,
    calculates scores, generates insights, and exports reports.
    """
    
    def __init__(
        self,
        github_token: Optional[str] = None,
        stackoverflow_key: Optional[str] = None,
        enable_linkedin_scraping: bool = False
    ):
        """
        Initialize FootprintScanner with optional API credentials.
        
        Args:
            github_token: GitHub Personal Access Token
            stackoverflow_key: Stack Exchange API key
            enable_linkedin_scraping: Enable LinkedIn scraping (default: False)
        """
        self.config = Config()
        
        # Initialize collectors
        self.github_collector = GitHubCollector(token=github_token)
        self.stackoverflow_collector = StackOverflowCollector(api_key=stackoverflow_key)
        self.linkedin_scraper = LinkedInScraper(enable_scraping=enable_linkedin_scraping)
        
        # Initialize scoring and insights
        self.scoring_engine = ScoringEngine()
        self.insights_generator = InsightsGenerator()
        
        logger.info("FootprintScanner initialized")
    
    def analyze_footprint(
        self,
        linkedin_url: Optional[str] = None,
        github_username: Optional[str] = None,
        stackoverflow_user_id: Optional[str] = None,
        stackoverflow_url: Optional[str] = None,
        linkedin_consent: bool = False,
        export_text: Optional[str] = None,
        export_json: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive digital footprint analysis.
        
        Args:
            linkedin_url: LinkedIn profile URL
            github_username: GitHub username
            stackoverflow_user_id: StackOverflow user ID or username
            linkedin_consent: User consent for LinkedIn scraping
            export_text: Path to export text report (optional)
            export_json: Path to export JSON report (optional)
            
        Returns:
            Complete footprint analysis including scores, insights, and data
        """
        logger.info("Starting footprint analysis...")
        
        analysis = {
            "scanned_at": datetime.now().isoformat(),
            "platforms_analyzed": [],
            "github_data": {},
            "stackoverflow_data": {},
            "linkedin_data": {},
            "scores": {},
            "insights": {},
            "success": False
        }
        
        # Normalize inputs
        # GitHub: allow pasting full profile URL, extract username
        if github_username and "github.com" in github_username:
            try:
                import re
                m = re.search(r"github\.com/([A-Za-z0-9-]+)(?:/)?$", github_username.strip())
                if not m:
                    # Fallback: last path segment
                    github_username = github_username.rstrip("/").split("/")[-1]
                else:
                    github_username = m.group(1)
                logger.info(f"Normalized GitHub username: {github_username}")
            except Exception:
                pass

        # Collect GitHub data
        if github_username:
            logger.info(f"Collecting GitHub data for: {github_username}")
            try:
                github_data = self.github_collector.collect(github_username)
                analysis["github_data"] = github_data
                if github_data.get("success"):
                    analysis["platforms_analyzed"].append("GitHub")
            except Exception as e:
                logger.error(f"GitHub collection failed: {str(e)}")
                analysis["github_data"] = {"success": False, "error": str(e)}
        
        # Backward-compat: allow passing StackOverflow profile URL and extract user id
        if not stackoverflow_user_id and stackoverflow_url:
            try:
                import re
                m = re.search(r"/users/(\d+)", stackoverflow_url)
                if m:
                    stackoverflow_user_id = m.group(1)
                    logger.info(f"Extracted StackOverflow user id: {stackoverflow_user_id}")
            except Exception:
                pass

        # Collect StackOverflow data (using user id if available)
        if stackoverflow_user_id:
            logger.info(f"Collecting StackOverflow data for: {stackoverflow_user_id}")
            try:
                so_data = self.stackoverflow_collector.collect(stackoverflow_user_id)
                analysis["stackoverflow_data"] = so_data
                if so_data.get("success"):
                    analysis["platforms_analyzed"].append("StackOverflow")
            except Exception as e:
                logger.error(f"StackOverflow collection failed: {str(e)}")
                analysis["stackoverflow_data"] = {"success": False, "error": str(e)}
        
        # Collect LinkedIn data
        if linkedin_url:
            logger.info(f"Collecting LinkedIn data for: {linkedin_url}")
            try:
                linkedin_data = self.linkedin_scraper.collect(
                    linkedin_url,
                    user_consent=linkedin_consent
                )
                analysis["linkedin_data"] = linkedin_data
                if linkedin_data.get("success"):
                    analysis["platforms_analyzed"].append("LinkedIn")
            except Exception as e:
                logger.error(f"LinkedIn collection failed: {str(e)}")
                analysis["linkedin_data"] = {"success": False, "error": str(e)}
        
        # Check if we have any data
        if not analysis["platforms_analyzed"]:
            logger.warning("No platform data collected successfully")
            analysis["error"] = "Failed to collect data from any platform"
            # Provide default empty scores/insights for UI compatibility
            analysis["scores"] = {"overall": 0, "ratings": {"overall": "N/A"}}
            analysis["insights"] = {
                "strengths": [],
                "areas_for_improvement": [],
                "recommendations": []
            }
            # Backward-compatibility fields
            try:
                summary = self.get_summary(analysis)
                analysis.update({
                    "overall_score": summary.get("overall_score", 0),
                    "strengths": analysis.get("insights", {}).get("strengths", []),
                    "areas_for_improvement": analysis.get("insights", {}).get("areas_for_improvement", []),
                    "recommendations": analysis.get("insights", {}).get("recommendations", []),
                })
            except Exception:
                pass
            return analysis
        
        # Calculate scores
        logger.info("Calculating scores...")
        try:
            scores = self.scoring_engine.calculate_scores(
                github_data=analysis["github_data"] if analysis["github_data"].get("success") else None,
                stackoverflow_data=analysis["stackoverflow_data"] if analysis["stackoverflow_data"].get("success") else None,
                linkedin_data=analysis["linkedin_data"] if analysis["linkedin_data"].get("success") else None
            )
            analysis["scores"] = scores
        except Exception as e:
            logger.error(f"Scoring failed: {str(e)}")
            analysis["scores"] = {"error": str(e)}
        
        # Generate insights
        logger.info("Generating insights...")
        try:
            insights = self.insights_generator.generate_insights(
                scores=analysis["scores"],
                github_data=analysis["github_data"] if analysis["github_data"].get("success") else None,
                stackoverflow_data=analysis["stackoverflow_data"] if analysis["stackoverflow_data"].get("success") else None,
                linkedin_data=analysis["linkedin_data"] if analysis["linkedin_data"].get("success") else None
            )
            analysis["insights"] = insights
        except Exception as e:
            logger.error(f"Insights generation failed: {str(e)}")
            analysis["insights"] = {"error": str(e)}
        
        analysis["success"] = True
        
        # Export reports if requested
        if export_text:
            logger.info(f"Exporting text report to: {export_text}")
            try:
                TextExporter.export(analysis, export_text)
            except Exception as e:
                logger.error(f"Text export failed: {str(e)}")
        
        if export_json:
            logger.info(f"Exporting JSON report to: {export_json}")
            try:
                JSONExporter.export(analysis, export_json)
            except Exception as e:
                logger.error(f"JSON export failed: {str(e)}")
        
        logger.info("Footprint analysis completed successfully")
        
        # Backward-compatibility: attach summary keys expected by legacy UI
        try:
            summary = self.get_summary(analysis)
            analysis.update({
                "overall_score": summary.get("overall_score", 0),
                "strengths": analysis.get("insights", {}).get("strengths", []),
                "areas_for_improvement": analysis.get("insights", {}).get("areas_for_improvement", []),
                "recommendations": analysis.get("insights", {}).get("recommendations", []),
            })
        except Exception:
            pass

        # Backward-compatibility: provide legacy platform blocks for UI tabs
        try:
            if linkedin_url:
                analysis["linkedin"] = self._analyze_linkedin(linkedin_url)
            if github_username:
                # Add some demo fields referenced by UI
                gh = self._analyze_github(github_username)
                # Enrich demo stats a bit if we have real data
                if analysis.get("github_data", {}).get("success"):
                    gh["score"] = summary.get("platform_scores", {}).get("github", gh.get("score", 0))
                analysis["github"] = gh
            if stackoverflow_url:
                analysis["stackoverflow"] = self._analyze_stackoverflow(stackoverflow_url)
        except Exception:
            pass

        return analysis
    
    def export_report(
        self,
        analysis: Dict[str, Any],
        format: str = "text",
        output_path: Optional[str] = None
    ) -> str:
        """
        Export analysis report in specified format.
        
        Args:
            analysis: Analysis data from analyze_footprint()
            format: Export format ("text" or "json")
            output_path: Path to save report
            
        Returns:
            Report content as string
        """
        if format.lower() == "json":
            return JSONExporter.export(analysis, output_path)
        else:
            return TextExporter.export(analysis, output_path)
    
    def get_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a summary of the analysis results.
        
        Args:
            analysis: Analysis data from analyze_footprint()
            
        Returns:
            Summary dictionary
        """
        scores = analysis.get("scores", {})
        insights = analysis.get("insights", {})
        
        return {
            "overall_score": scores.get("overall", 0),
            "overall_rating": scores.get("ratings", {}).get("overall", "N/A"),
            "platforms_analyzed": analysis.get("platforms_analyzed", []),
            "platform_scores": {
                "github": scores.get("github", 0),
                "stackoverflow": scores.get("stackoverflow", 0),
                "linkedin": scores.get("linkedin", 0)
            },
            "top_strengths": insights.get("strengths", [])[:3],
            "top_improvements": insights.get("areas_for_improvement", [])[:3],
            "top_recommendations": insights.get("recommendations", [])[:3]
        }


# Legacy methods for backward compatibility with existing Streamlit app
    def _analyze_linkedin(self, url: str) -> Dict[str, Any]:
        """Legacy method - use analyze_footprint() instead."""
        import re
        
        analysis = {
            "platform": "LinkedIn",
            "url": url,
            "is_valid": bool(re.match(r'(https?://)?(www\.)?linkedin\.com/(in|profile)/[\w-]+', url or "")),
            "score": 60,
            "insights": [
                {"category": "Profile Completeness", "status": "Good", "description": "Profile URL is valid"},
            ],
            "recommendations": [
                "Complete all profile sections",
                "Add professional photo",
                "Request skill endorsements"
            ]
        }
        return analysis
    
    def _analyze_github(self, username: str) -> Dict[str, Any]:
        """Legacy method - use analyze_footprint() instead."""
        import re
        
        analysis = {
            "platform": "GitHub",
            "username": username,
            "is_valid": bool(re.match(r'^[a-zA-Z0-9-]+$', username or "")) and len(username or "") <= 39,
            "score": 65,
            "insights": [
                {"category": "Repository Quality", "status": "To be analyzed", "description": "Connect API"},
            ],
            "recommendations": [
                "Maintain consistent contributions",
                "Create pinned repositories",
                "Write comprehensive READMEs"
            ],
            "demo_stats": {
                "profile_url": f"https://github.com/{username}",
                "activity_level": "Moderate"
            }
        }
        return analysis
    
    def _analyze_stackoverflow(self, url: str) -> Dict[str, Any]:
        """Legacy method - use analyze_footprint() instead."""
        import re
        
        analysis = {
            "platform": "StackOverflow",
            "url": url,
            "is_valid": bool(re.match(r'(https?://)?(www\.)?stackoverflow\.com/users/\d+/[\w-]+', url or "")),
            "score": 55,
            "insights": [
                {"category": "Reputation Score", "status": "To be analyzed", "description": "Connect API"},
            ],
            "recommendations": [
                "Answer questions regularly",
                "Earn badges",
                "Build reputation"
            ],
            "demo_stats": {
                "reputation": "To be fetched via API"
            }
        }
        return analysis
    
    def _validate_linkedin_url(self, url: str) -> bool:
        """Validate LinkedIn URL format"""
        import re
        if not url:
            return False
        pattern = r'(https?://)?(www\.)?linkedin\.com/(in|profile)/[\w-]+'
        return bool(re.match(pattern, url))
    
    def _validate_github_username(self, username: str) -> bool:
        """Validate GitHub username format"""
        import re
        if not username:
            return False
        pattern = r'^[a-zA-Z0-9-]+$'
        return bool(re.match(pattern, username)) and len(username) <= 39
    
    def _validate_stackoverflow_url(self, url: str) -> bool:
        """Validate StackOverflow URL format"""
        import re
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
        
        platforms_count = len(results.get("platforms_analyzed", []))
        
        if platforms_count == 0:
            recommendations.append({
                "priority": "Critical",
                "recommendation": "Create profiles on professional platforms",
                "impact": "Establishes professional online presence"
            })
        
        return recommendations
    
    def _analyze_strengths_weaknesses(
        self,
        results: Dict[str, Any]
    ) -> tuple:
        """Analyze strengths and areas for improvement"""
        strengths = []
        improvements = []
        
        platforms_count = len(results.get("platforms_analyzed", []))
        
        if platforms_count >= 2:
            strengths.append("Good platform diversity")
        else:
            improvements.append("Limited platform presence")
        
        return strengths, improvements
    
    def generate_footprint_report(
        self,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive footprint report"""
        return self.get_summary(analysis)
    
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

