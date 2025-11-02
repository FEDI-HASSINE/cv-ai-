"""
Scoring Engine
Calculates scores for each platform and overall footprint score.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Calculates comprehensive scores for digital footprint analysis.
    
    Scoring methodology:
    - GitHub: repos, stars, contributions, followers, languages
    - StackOverflow: reputation, badges, answers, questions
    - LinkedIn: profile completeness, connections, experience, skills
    - Overall: weighted average across platforms
    """
    
    # Scoring weights for each platform (customizable)
    WEIGHTS = {
        "github": 0.35,
        "stackoverflow": 0.35,
        "linkedin": 0.30
    }
    
    def __init__(self):
        """Initialize scoring engine."""
        pass
    
    def calculate_scores(
        self,
        github_data: Optional[Dict[str, Any]] = None,
        stackoverflow_data: Optional[Dict[str, Any]] = None,
        linkedin_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate scores for all platforms.
        
        Args:
            github_data: GitHub collector data
            stackoverflow_data: StackOverflow collector data
            linkedin_data: LinkedIn scraper data
            
        Returns:
            Dictionary with scores for each platform and overall score
        """
        scores = {
            "github": 0,
            "stackoverflow": 0,
            "linkedin": 0,
            "overall": 0,
            "breakdown": {},
            "calculated_at": datetime.now().isoformat()
        }
        
        platform_scores = []
        
        # Calculate GitHub score
        if github_data and github_data.get("success"):
            github_score, github_breakdown = self._score_github(github_data)
            scores["github"] = github_score
            scores["breakdown"]["github"] = github_breakdown
            platform_scores.append(("github", github_score))
        
        # Calculate StackOverflow score
        if stackoverflow_data and stackoverflow_data.get("success"):
            so_score, so_breakdown = self._score_stackoverflow(stackoverflow_data)
            scores["stackoverflow"] = so_score
            scores["breakdown"]["stackoverflow"] = so_breakdown
            platform_scores.append(("stackoverflow", so_score))
        
        # Calculate LinkedIn score
        if linkedin_data and linkedin_data.get("success"):
            linkedin_score, linkedin_breakdown = self._score_linkedin(linkedin_data)
            scores["linkedin"] = linkedin_score
            scores["breakdown"]["linkedin"] = linkedin_breakdown
            platform_scores.append(("linkedin", linkedin_score))
        
        # Calculate overall score (weighted average)
        if platform_scores:
            scores["overall"] = self._calculate_overall_score(platform_scores)
        
        # Add ratings
        scores["ratings"] = self._get_ratings(scores)
        
        return scores
    
    def _score_github(self, data: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
        """
        Calculate GitHub score (0-100).
        
        Factors:
        - Public repos (20 points)
        - Stars received (25 points)
        - Followers (20 points)
        - Recent activity (20 points)
        - Language diversity (15 points)
        """
        score = 0
        breakdown = {}
        
        stats = data.get("statistics", {})
        repos = data.get("repositories", {})
        languages = data.get("languages", {})
        
        # Public repos score (0-20)
        public_repos = stats.get("public_repos", 0)
        repos_score = min(20, (public_repos / 20) * 20)
        score += repos_score
        breakdown["repos"] = {
            "score": round(repos_score, 1),
            "count": public_repos
        }
        
        # Stars score (0-25)
        total_stars = stats.get("total_stars", 0)
        stars_score = min(25, (total_stars / 100) * 25)
        score += stars_score
        breakdown["stars"] = {
            "score": round(stars_score, 1),
            "count": total_stars
        }
        
        # Followers score (0-20)
        followers = stats.get("followers", 0)
        followers_score = min(20, (followers / 100) * 20)
        score += followers_score
        breakdown["followers"] = {
            "score": round(followers_score, 1),
            "count": followers
        }
        
        # Recent activity score (0-20)
        recent = repos.get("recent_activity", {})
        repos_updated = recent.get("repos_updated", 0)
        activity_score = min(20, (repos_updated / 5) * 20)
        score += activity_score
        breakdown["activity"] = {
            "score": round(activity_score, 1),
            "repos_updated_30d": repos_updated
        }
        
        # Language diversity score (0-15)
        lang_count = len(languages)
        diversity_score = min(15, (lang_count / 5) * 15)
        score += diversity_score
        breakdown["languages"] = {
            "score": round(diversity_score, 1),
            "count": lang_count,
            "top": list(languages.keys())[:5]
        }
        
        return round(score), breakdown
    
    def _score_stackoverflow(self, data: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
        """
        Calculate StackOverflow score (0-100).
        
        Factors:
        - Reputation (30 points)
        - Badges (25 points)
        - Answer quality (25 points)
        - Question quality (10 points)
        - Tags expertise (10 points)
        """
        score = 0
        breakdown = {}
        
        reputation = data.get("reputation", {})
        badges = data.get("badges", {})
        activity = data.get("activity", {})
        tags = data.get("tags", {})
        
        # Reputation score (0-30)
        rep_score_value = reputation.get("score", 0)
        # Using logarithmic scale for reputation
        if rep_score_value > 0:
            import math
            rep_score = min(30, (math.log10(rep_score_value + 1) / 5) * 30)
        else:
            rep_score = 0
        score += rep_score
        breakdown["reputation"] = {
            "score": round(rep_score, 1),
            "value": rep_score_value
        }
        
        # Badges score (0-25)
        total_badges = badges.get("total", 0)
        gold = badges.get("gold", 0)
        silver = badges.get("silver", 0)
        # Weighted badge score
        badge_score = min(25, ((gold * 3 + silver * 2 + total_badges) / 50) * 25)
        score += badge_score
        breakdown["badges"] = {
            "score": round(badge_score, 1),
            "gold": gold,
            "silver": silver,
            "bronze": badges.get("bronze", 0),
            "total": total_badges
        }
        
        # Answer quality score (0-25)
        answers = activity.get("answers", {})
        answer_count = answers.get("count", 0)
        answer_score_value = answers.get("score", 0)
        accepted = answers.get("accepted", 0)
        
        # Calculate based on count, score, and acceptance rate
        if answer_count > 0:
            acceptance_rate = accepted / answer_count
            answer_quality = min(25, (
                (answer_count / 50) * 10 +  # Count component
                (answer_score_value / 100) * 10 +  # Score component
                (acceptance_rate * 5)  # Acceptance rate component
            ))
        else:
            answer_quality = 0
        
        score += answer_quality
        breakdown["answers"] = {
            "score": round(answer_quality, 1),
            "count": answer_count,
            "total_score": answer_score_value,
            "accepted": accepted
        }
        
        # Question quality score (0-10)
        questions = activity.get("questions", {})
        question_count = questions.get("count", 0)
        question_score_value = questions.get("score", 0)
        question_quality = min(10, (question_count / 20) * 5 + (question_score_value / 50) * 5)
        score += question_quality
        breakdown["questions"] = {
            "score": round(question_quality, 1),
            "count": question_count,
            "total_score": question_score_value
        }
        
        # Tags expertise score (0-10)
        top_tags = tags.get("top_tags", [])
        tag_count = len(top_tags)
        tags_score = min(10, (tag_count / 10) * 10)
        score += tags_score
        breakdown["tags"] = {
            "score": round(tags_score, 1),
            "count": tag_count,
            "top": [tag.get("name") for tag in top_tags[:5]]
        }
        
        return round(score), breakdown
    
    def _score_linkedin(self, data: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
        """
        Calculate LinkedIn score (0-100).
        
        Factors:
        - Profile completeness (30 points)
        - Experience depth (30 points)
        - Education (20 points)
        - Skills (20 points)
        """
        score = 0
        breakdown = {}
        
        profile = data.get("profile", {})
        experience = data.get("experience", [])
        education = data.get("education", [])
        skills = data.get("skills", [])
        
        # Profile completeness score (0-30)
        profile_fields = ["name", "headline", "location", "about"]
        filled_fields = sum(1 for field in profile_fields if profile.get(field))
        completeness_score = (filled_fields / len(profile_fields)) * 30
        score += completeness_score
        breakdown["profile_completeness"] = {
            "score": round(completeness_score, 1),
            "filled_fields": filled_fields,
            "total_fields": len(profile_fields)
        }
        
        # Experience score (0-30)
        exp_count = len(experience)
        experience_score = min(30, (exp_count / 5) * 30)
        score += experience_score
        breakdown["experience"] = {
            "score": round(experience_score, 1),
            "count": exp_count
        }
        
        # Education score (0-20)
        edu_count = len(education)
        education_score = min(20, (edu_count / 3) * 20)
        score += education_score
        breakdown["education"] = {
            "score": round(education_score, 1),
            "count": edu_count
        }
        
        # Skills score (0-20)
        skill_count = len(skills)
        skills_score = min(20, (skill_count / 10) * 20)
        score += skills_score
        breakdown["skills"] = {
            "score": round(skills_score, 1),
            "count": skill_count
        }
        
        return round(score), breakdown
    
    def _calculate_overall_score(self, platform_scores: list) -> int:
        """
        Calculate weighted overall score.
        
        Args:
            platform_scores: List of (platform_name, score) tuples
            
        Returns:
            Overall weighted score (0-100)
        """
        if not platform_scores:
            return 0
        
        # Calculate weighted average
        total_weight = sum(self.WEIGHTS.get(platform, 0) for platform, _ in platform_scores)
        
        if total_weight == 0:
            # Fallback to simple average
            return round(sum(score for _, score in platform_scores) / len(platform_scores))
        
        weighted_sum = sum(
            score * self.WEIGHTS.get(platform, 0)
            for platform, score in platform_scores
        )
        
        return round(weighted_sum / total_weight)
    
    def _get_ratings(self, scores: Dict[str, Any]) -> Dict[str, str]:
        """
        Get text ratings for scores.
        
        Args:
            scores: Score dictionary
            
        Returns:
            Dictionary with text ratings
        """
        def rate(score: int) -> str:
            if score >= 90:
                return "Excellent"
            elif score >= 75:
                return "Very Good"
            elif score >= 60:
                return "Good"
            elif score >= 40:
                return "Fair"
            elif score >= 20:
                return "Needs Improvement"
            else:
                return "Limited Presence"
        
        return {
            "github": rate(scores.get("github", 0)),
            "stackoverflow": rate(scores.get("stackoverflow", 0)),
            "linkedin": rate(scores.get("linkedin", 0)),
            "overall": rate(scores.get("overall", 0))
        }
