"""
Text Exporter
Exports footprint analysis to human-readable text format.
"""

import logging
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class TextExporter:
    """
    Exports footprint analysis to formatted text report.
    """
    
    @staticmethod
    def export(
        data: Dict[str, Any],
        output_path: str = None
    ) -> str:
        """
        Export footprint analysis to text format.
        
        Args:
            data: Complete footprint analysis data
            output_path: Optional path to save text file
            
        Returns:
            Formatted text string
        """
        try:
            # Build text report
            report_lines = []
            
            # Header
            report_lines.extend(TextExporter._build_header(data))
            report_lines.append("")
            
            # Scores section
            report_lines.extend(TextExporter._build_scores_section(data.get("scores", {})))
            report_lines.append("")
            
            # Insights section
            report_lines.extend(TextExporter._build_insights_section(data.get("insights", {})))
            report_lines.append("")
            
            # Platform details
            if data.get("github_data", {}).get("success"):
                report_lines.extend(TextExporter._build_github_section(data))
                report_lines.append("")
            
            if data.get("stackoverflow_data", {}).get("success"):
                report_lines.extend(TextExporter._build_stackoverflow_section(data))
                report_lines.append("")
            
            if data.get("linkedin_data", {}).get("success"):
                report_lines.extend(TextExporter._build_linkedin_section(data))
                report_lines.append("")
            
            # 30-day action plan
            report_lines.extend(TextExporter._build_action_plan_section(data.get("insights", {})))
            report_lines.append("")
            
            # Footer
            report_lines.extend(TextExporter._build_footer())
            
            # Join all lines
            report_text = "\n".join(report_lines)
            
            # Save to file if path provided
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                
                logger.info(f"Text report saved to: {output_path}")
            
            return report_text
            
        except Exception as e:
            logger.error(f"Error exporting text: {str(e)}")
            raise
    
    @staticmethod
    def _build_header(data: Dict[str, Any]) -> List[str]:
        """Build report header."""
        lines = []
        lines.append("=" * 80)
        lines.append("DIGITAL FOOTPRINT ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Target information
        github_data = data.get("github_data", {})
        stackoverflow_data = data.get("stackoverflow_data", {})
        linkedin_data = data.get("linkedin_data", {})
        
        lines.append("")
        lines.append("Target Profiles:")
        
        if github_data.get("success"):
            lines.append(f"  • GitHub: {github_data.get('username')}")
        
        if stackoverflow_data.get("success"):
            profile = stackoverflow_data.get("profile", {})
            lines.append(f"  • StackOverflow: {profile.get('display_name')} (ID: {stackoverflow_data.get('user_id')})")
        
        if linkedin_data.get("success"):
            lines.append(f"  • LinkedIn: {linkedin_data.get('url')}")
        
        return lines
    
    @staticmethod
    def _build_scores_section(scores: Dict[str, Any]) -> List[str]:
        """Build scores section."""
        lines = []
        lines.append("-" * 80)
        lines.append("OVERALL SCORES")
        lines.append("-" * 80)
        lines.append("")
        
        overall = scores.get("overall", 0)
        ratings = scores.get("ratings", {})
        
        lines.append(f"Overall Score: {overall}/100 - {ratings.get('overall', 'N/A')}")
        lines.append("")
        lines.append("Platform Scores:")
        
        platform_scores = [
            ("GitHub", scores.get("github", 0), ratings.get("github", "N/A")),
            ("StackOverflow", scores.get("stackoverflow", 0), ratings.get("stackoverflow", "N/A")),
            ("LinkedIn", scores.get("linkedin", 0), ratings.get("linkedin", "N/A"))
        ]
        
        for platform, score, rating in platform_scores:
            bar = TextExporter._create_progress_bar(score)
            lines.append(f"  {platform:15} {score:3d}/100  {bar}  {rating}")
        
        return lines
    
    @staticmethod
    def _build_insights_section(insights: Dict[str, Any]) -> List[str]:
        """Build insights section."""
        lines = []
        lines.append("-" * 80)
        lines.append("KEY INSIGHTS")
        lines.append("-" * 80)
        lines.append("")
        
        # Strengths
        strengths = insights.get("strengths", [])
        if strengths:
            lines.append("✓ STRENGTHS:")
            for strength in strengths[:8]:
                lines.append(f"  • {strength}")
            lines.append("")
        
        # Areas for improvement
        improvements = insights.get("areas_for_improvement", [])
        if improvements:
            lines.append("⚠ AREAS FOR IMPROVEMENT:")
            for improvement in improvements[:8]:
                lines.append(f"  • {improvement}")
            lines.append("")
        
        # Recommendations
        recommendations = insights.get("recommendations", [])
        if recommendations:
            lines.append("💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"  {i}. {rec}")
        
        return lines
    
    @staticmethod
    def _build_github_section(data: Dict[str, Any]) -> List[str]:
        """Build GitHub details section."""
        lines = []
        github_data = data.get("github_data", {})
        insights = data.get("insights", {}).get("platform_insights", {}).get("github", {})
        
        lines.append("-" * 80)
        lines.append("GITHUB ANALYSIS")
        lines.append("-" * 80)
        lines.append("")
        
        profile = github_data.get("profile", {})
        stats = github_data.get("statistics", {})
        
        # Profile info
        if profile.get("name"):
            lines.append(f"Name: {profile.get('name')}")
        if profile.get("bio"):
            lines.append(f"Bio: {profile.get('bio')}")
        if profile.get("location"):
            lines.append(f"Location: {profile.get('location')}")
        lines.append("")
        
        # Statistics
        lines.append("Statistics:")
        lines.append(f"  • Public Repositories: {stats.get('public_repos', 0)}")
        lines.append(f"  • Total Stars: {stats.get('total_stars', 0)}")
        lines.append(f"  • Followers: {stats.get('followers', 0)}")
        lines.append(f"  • Following: {stats.get('following', 0)}")
        lines.append("")
        
        # Top languages
        languages = github_data.get("languages", {})
        if languages:
            lines.append("Top Languages:")
            for lang, count in list(languages.items())[:5]:
                lines.append(f"  • {lang}: {count} repositories")
            lines.append("")
        
        # Top repositories
        repos = github_data.get("repositories", {}).get("top_repos", [])
        if repos:
            lines.append("Top Repositories:")
            for repo in repos[:3]:
                lines.append(f"  • {repo.get('name')} - ⭐ {repo.get('stars')} stars")
                if repo.get("description"):
                    lines.append(f"    {repo.get('description')[:80]}")
            lines.append("")
        
        # GitHub-specific insights
        tips = insights.get("tips", [])
        if tips:
            lines.append("GitHub Tips:")
            for tip in tips[:3]:
                lines.append(f"  💡 {tip}")
        
        return lines
    
    @staticmethod
    def _build_stackoverflow_section(data: Dict[str, Any]) -> List[str]:
        """Build StackOverflow details section."""
        lines = []
        so_data = data.get("stackoverflow_data", {})
        insights = data.get("insights", {}).get("platform_insights", {}).get("stackoverflow", {})
        
        lines.append("-" * 80)
        lines.append("STACKOVERFLOW ANALYSIS")
        lines.append("-" * 80)
        lines.append("")
        
        profile = so_data.get("profile", {})
        reputation = so_data.get("reputation", {})
        badges = so_data.get("badges", {})
        activity = so_data.get("activity", {})
        
        # Profile info
        lines.append(f"Display Name: {profile.get('display_name')}")
        if profile.get("location"):
            lines.append(f"Location: {profile.get('location')}")
        lines.append("")
        
        # Reputation
        lines.append(f"Reputation: {reputation.get('score', 0):,}")
        lines.append(f"  • Change this year: +{reputation.get('reputation_change_year', 0)}")
        lines.append(f"  • Change this month: +{reputation.get('reputation_change_month', 0)}")
        lines.append("")
        
        # Badges
        lines.append("Badges:")
        lines.append(f"  • Gold: {badges.get('gold', 0)}")
        lines.append(f"  • Silver: {badges.get('silver', 0)}")
        lines.append(f"  • Bronze: {badges.get('bronze', 0)}")
        lines.append(f"  • Total: {badges.get('total', 0)}")
        lines.append("")
        
        # Activity
        answers = activity.get("answers", {})
        questions = activity.get("questions", {})
        
        lines.append("Activity:")
        lines.append(f"  • Answers: {answers.get('count', 0)} (Score: {answers.get('score', 0)})")
        lines.append(f"  • Accepted Answers: {answers.get('accepted', 0)}")
        lines.append(f"  • Questions: {questions.get('count', 0)} (Score: {questions.get('score', 0)})")
        lines.append("")
        
        # Top tags
        tags = so_data.get("tags", {}).get("top_tags", [])
        if tags:
            lines.append("Top Tags:")
            for tag in tags[:5]:
                lines.append(f"  • {tag.get('name')} - {tag.get('answer_count', 0)} answers")
            lines.append("")
        
        # StackOverflow-specific insights
        tips = insights.get("tips", [])
        if tips:
            lines.append("StackOverflow Tips:")
            for tip in tips[:3]:
                lines.append(f"  💡 {tip}")
        
        return lines
    
    @staticmethod
    def _build_linkedin_section(data: Dict[str, Any]) -> List[str]:
        """Build LinkedIn details section."""
        lines = []
        linkedin_data = data.get("linkedin_data", {})
        insights = data.get("insights", {}).get("platform_insights", {}).get("linkedin", {})
        
        lines.append("-" * 80)
        lines.append("LINKEDIN ANALYSIS")
        lines.append("-" * 80)
        lines.append("")
        
        profile = linkedin_data.get("profile", {})
        experience = linkedin_data.get("experience", [])
        education = linkedin_data.get("education", [])
        skills = linkedin_data.get("skills", [])
        
        # Profile info
        if profile.get("name"):
            lines.append(f"Name: {profile.get('name')}")
        if profile.get("headline"):
            lines.append(f"Headline: {profile.get('headline')}")
        if profile.get("location"):
            lines.append(f"Location: {profile.get('location')}")
        lines.append("")
        
        # Experience
        if experience:
            lines.append(f"Work Experience ({len(experience)} positions):")
            for exp in experience[:3]:
                lines.append(f"  • {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
                if exp.get("duration"):
                    lines.append(f"    {exp.get('duration')}")
            lines.append("")
        
        # Education
        if education:
            lines.append(f"Education ({len(education)} entries):")
            for edu in education:
                lines.append(f"  • {edu.get('school', 'N/A')}")
                if edu.get("degree"):
                    lines.append(f"    {edu.get('degree')}")
            lines.append("")
        
        # Skills
        if skills:
            lines.append(f"Skills ({len(skills)} listed):")
            skill_list = ", ".join(skills[:15])
            lines.append(f"  {skill_list}")
            if len(skills) > 15:
                lines.append(f"  ... and {len(skills) - 15} more")
            lines.append("")
        
        # LinkedIn-specific insights
        tips = insights.get("tips", [])
        if tips:
            lines.append("LinkedIn Tips:")
            for tip in tips[:3]:
                lines.append(f"  💡 {tip}")
        
        return lines
    
    @staticmethod
    def _build_action_plan_section(insights: Dict[str, Any]) -> List[str]:
        """Build 30-day action plan section."""
        lines = []
        action_plan = insights.get("30_day_plan", [])
        
        if not action_plan:
            return lines
        
        lines.append("=" * 80)
        lines.append("30-DAY ACTION PLAN")
        lines.append("=" * 80)
        lines.append("")
        
        # Group by week
        weeks = {}
        for action in action_plan:
            week = action.get("week", 1)
            if week not in weeks:
                weeks[week] = []
            weeks[week].append(action)
        
        # Print by week
        for week_num in sorted(weeks.keys()):
            lines.append(f"WEEK {week_num}")
            lines.append("-" * 40)
            
            for action in weeks[week_num]:
                day = action.get("day")
                priority = action.get("priority", "medium").upper()
                action_text = action.get("action")
                time_est = action.get("estimated_time", "N/A")
                platforms = ", ".join(action.get("platforms", []))
                
                lines.append(f"Day {day} [{priority}]")
                lines.append(f"  Action: {action_text}")
                lines.append(f"  Time: {time_est} | Platforms: {platforms}")
                lines.append("")
        
        return lines
    
    @staticmethod
    def _build_footer() -> List[str]:
        """Build report footer."""
        lines = []
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        lines.append("")
        lines.append("Generated by CV-AI Footprint Scanner")
        lines.append("For questions or feedback, please contact the development team.")
        return lines
    
    @staticmethod
    def _create_progress_bar(score: int, width: int = 20) -> str:
        """Create a text-based progress bar."""
        filled = int((score / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
