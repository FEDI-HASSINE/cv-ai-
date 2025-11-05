"""
JSON Exporter
Exports footprint analysis to structured JSON format.
"""

import json
import logging
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class JSONExporter:
    """
    Exports footprint analysis to JSON format following the specified schema.
    """
    
    @staticmethod
    def export(
        data: Dict[str, Any],
        output_path: str = None
    ) -> str:
        """
        Export footprint analysis to JSON.
        
        Args:
            data: Complete footprint analysis data
            output_path: Optional path to save JSON file
            
        Returns:
            JSON string
        """
        try:
            # Build JSON structure
            json_data = JSONExporter._build_json_structure(data)
            
            # Convert to JSON string with pretty formatting
            json_string = json.dumps(json_data, indent=2, ensure_ascii=False)
            
            # Save to file if path provided
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(json_string)
                
                logger.info(f"JSON report saved to: {output_path}")
            
            return json_string
            
        except Exception as e:
            logger.error(f"Error exporting JSON: {str(e)}")
            raise
    
    @staticmethod
    def _build_json_structure(data: Dict[str, Any]) -> Dict[str, Any]:
        """Build the JSON structure following the specified schema."""
        
        scores = data.get("scores", {})
        insights = data.get("insights", {})
        github_data = data.get("github_data", {})
        stackoverflow_data = data.get("stackoverflow_data", {})
        linkedin_data = data.get("linkedin_data", {})
        
        # Build meta section
        meta = {
            "scanned_at": data.get("scanned_at", datetime.now().isoformat()),
            "target": {
                "github": github_data.get("username") if github_data.get("success") else None,
                "linkedin": linkedin_data.get("url") if linkedin_data.get("success") else None,
                "stackoverflow": stackoverflow_data.get("user_id") if stackoverflow_data.get("success") else None
            },
            "platforms_analyzed": []
        }
        
        # Add analyzed platforms
        if github_data.get("success"):
            meta["platforms_analyzed"].append("GitHub")
        if stackoverflow_data.get("success"):
            meta["platforms_analyzed"].append("StackOverflow")
        if linkedin_data.get("success"):
            meta["platforms_analyzed"].append("LinkedIn")
        
        # Build scores section
        scores_section = {
            "github": scores.get("github", 0),
            "stackoverflow": scores.get("stackoverflow", 0),
            "linkedin": scores.get("linkedin", 0),
            "overall": scores.get("overall", 0),
            "ratings": scores.get("ratings", {}),
            "breakdown": scores.get("breakdown", {})
        }
        
        # Build insights section
        insights_section = {
            "strengths": insights.get("strengths", []),
            "areas_for_improvement": insights.get("areas_for_improvement", []),
            "recommendations": insights.get("recommendations", [])
        }
        
        # Build platform insights
        platform_insights = {}
        
        if github_data.get("success"):
            platform_insights["github"] = {
                "data": JSONExporter._format_github_data(github_data),
                "insights": insights.get("platform_insights", {}).get("github", {})
            }
        
        if stackoverflow_data.get("success"):
            platform_insights["stackoverflow"] = {
                "data": JSONExporter._format_stackoverflow_data(stackoverflow_data),
                "insights": insights.get("platform_insights", {}).get("stackoverflow", {})
            }
        
        if linkedin_data.get("success"):
            platform_insights["linkedin"] = {
                "data": JSONExporter._format_linkedin_data(linkedin_data),
                "insights": insights.get("platform_insights", {}).get("linkedin", {})
            }
        
        # Build 30-day plan
        action_plan = insights.get("30_day_plan", [])
        
        # Assemble final structure
        json_structure = {
            "meta": meta,
            "scores": scores_section,
            "insights": insights_section,
            "platform_insights": platform_insights,
            "30_day_plan": action_plan,
            "generated_at": datetime.now().isoformat()
        }
        
        return json_structure
    
    @staticmethod
    def _format_github_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format GitHub data for JSON export."""
        return {
            "username": data.get("username"),
            "profile": data.get("profile", {}),
            "statistics": data.get("statistics", {}),
            "repositories": {
                "total": data.get("repositories", {}).get("total", 0),
                "top_repos": data.get("repositories", {}).get("top_repos", [])[:5]
            },
            "languages": data.get("languages", {}),
            "collected_at": data.get("collected_at")
        }
    
    @staticmethod
    def _format_stackoverflow_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format StackOverflow data for JSON export."""
        return {
            "user_id": data.get("user_id"),
            "profile": data.get("profile", {}),
            "reputation": data.get("reputation", {}),
            "badges": data.get("badges", {}),
            "activity": {
                "answers": data.get("activity", {}).get("answers", {}),
                "questions": data.get("activity", {}).get("questions", {})
            },
            "tags": {
                "top_tags": data.get("tags", {}).get("top_tags", [])[:10]
            },
            "collected_at": data.get("collected_at")
        }
    
    @staticmethod
    def _format_linkedin_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format LinkedIn data for JSON export."""
        return {
            "url": data.get("url"),
            "profile": data.get("profile", {}),
            "experience": data.get("experience", []),
            "education": data.get("education", []),
            "skills": data.get("skills", []),
            "collected_at": data.get("collected_at")
        }
