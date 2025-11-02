"""
StackOverflow Data Collector
Uses Stack Exchange API to collect user reputation, badges, tags, and answers.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class StackOverflowCollector:
    """
    Collects data from Stack Exchange API for StackOverflow users.
    """
    
    BASE_URL = "https://api.stackexchange.com/2.3"
    SITE = "stackoverflow"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize StackOverflow collector.
        
        Args:
            api_key: Stack Exchange API key (optional but increases rate limits)
        """
        self.api_key = api_key or os.getenv("STACKOVERFLOW_KEY")
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        # Headers
        headers = {
            "Accept": "application/json",
            "User-Agent": "cv-ai-footprint-scanner/1.0"
        }
        session.headers.update(headers)
        
        return session
    
    def collect(self, user_id: str) -> Dict[str, Any]:
        """
        Collect comprehensive StackOverflow data for a user.
        
        Args:
            user_id: StackOverflow user ID or username
            
        Returns:
            Dictionary containing StackOverflow profile data and statistics
        """
        try:
            logger.info(f"Collecting StackOverflow data for user: {user_id}")
            
            # Try to get user info (user_id might be numeric ID or username)
            user_data = self._get_user_info(user_id)
            if not user_data:
                return {"error": "User not found", "success": False}
            
            # Get the numeric user ID
            numeric_id = user_data["user_id"]
            
            # Get badges
            badges_data = self._get_badges(numeric_id)
            
            # Get top tags
            tags_data = self._get_top_tags(numeric_id)
            
            # Get top answers
            answers_data = self._get_top_answers(numeric_id)
            
            # Get questions
            questions_data = self._get_questions(numeric_id)
            
            result = {
                "success": True,
                "user_id": numeric_id,
                "profile": {
                    "display_name": user_data.get("display_name"),
                    "profile_image": user_data.get("profile_image"),
                    "link": user_data.get("link"),
                    "location": user_data.get("location"),
                    "website_url": user_data.get("website_url"),
                    "about_me": user_data.get("about_me", "")[:500],  # Truncate
                    "creation_date": self._format_timestamp(user_data.get("creation_date")),
                    "last_access_date": self._format_timestamp(user_data.get("last_access_date"))
                },
                "reputation": {
                    "score": user_data.get("reputation", 0),
                    "reputation_change_year": user_data.get("reputation_change_year", 0),
                    "reputation_change_quarter": user_data.get("reputation_change_quarter", 0),
                    "reputation_change_month": user_data.get("reputation_change_month", 0),
                    "reputation_change_week": user_data.get("reputation_change_week", 0),
                    "reputation_change_day": user_data.get("reputation_change_day", 0)
                },
                "badges": {
                    "gold": user_data.get("badge_counts", {}).get("gold", 0),
                    "silver": user_data.get("badge_counts", {}).get("silver", 0),
                    "bronze": user_data.get("badge_counts", {}).get("bronze", 0),
                    "total": sum(user_data.get("badge_counts", {}).values()),
                    "recent_badges": badges_data[:10]
                },
                "activity": {
                    "questions": {
                        "count": questions_data["total"],
                        "score": questions_data["total_score"],
                        "top_questions": questions_data["top_questions"]
                    },
                    "answers": {
                        "count": answers_data["total"],
                        "score": answers_data["total_score"],
                        "accepted": answers_data["accepted_count"],
                        "top_answers": answers_data["top_answers"]
                    }
                },
                "tags": {
                    "top_tags": tags_data[:15],
                    "total_tags": len(tags_data)
                },
                "statistics": {
                    "account_age_days": self._calculate_account_age(user_data.get("creation_date")),
                    "accept_rate": user_data.get("accept_rate", 0),
                    "is_employee": user_data.get("is_employee", False)
                },
                "collected_at": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully collected StackOverflow data for user {numeric_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error collecting StackOverflow data: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id
            }
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to Stack Exchange API."""
        if params is None:
            params = {}
        
        # Add required parameters
        params["site"] = self.SITE
        if self.api_key:
            params["key"] = self.api_key
        
        try:
            response = self.session.get(f"{self.BASE_URL}/{endpoint}", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if "error_id" in data:
                logger.error(f"Stack Exchange API error: {data.get('error_message')}")
                return {"items": []}
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {"items": []}
    
    def _get_user_info(self, user_identifier: str) -> Optional[Dict[str, Any]]:
        """Get user profile information by ID or username."""
        # First, try as numeric ID
        if user_identifier.isdigit():
            data = self._make_request(f"users/{user_identifier}", {"filter": "!--1nZv)deGu1"})
            if data.get("items"):
                return data["items"][0]
        
        # Try searching by display name
        data = self._make_request("users", {
            "inname": user_identifier,
            "filter": "!--1nZv)deGu1"
        })
        
        if data.get("items"):
            return data["items"][0]
        
        return None
    
    def _get_badges(self, user_id: int, page_size: int = 30) -> List[Dict[str, Any]]:
        """Get user's badges."""
        data = self._make_request(
            f"users/{user_id}/badges",
            {
                "order": "desc",
                "sort": "awarded",
                "pagesize": page_size
            }
        )
        
        badges = []
        for badge in data.get("items", []):
            badges.append({
                "name": badge.get("name"),
                "rank": badge.get("rank"),
                "badge_type": badge.get("badge_type"),
                "award_count": badge.get("award_count", 1),
                "link": badge.get("link")
            })
        
        return badges
    
    def _get_top_tags(self, user_id: int, page_size: int = 20) -> List[Dict[str, Any]]:
        """Get user's top tags."""
        data = self._make_request(
            f"users/{user_id}/top-tags",
            {"pagesize": page_size}
        )
        
        tags = []
        for tag in data.get("items", []):
            tags.append({
                "name": tag.get("tag_name"),
                "answer_count": tag.get("answer_count", 0),
                "answer_score": tag.get("answer_score", 0),
                "question_count": tag.get("question_count", 0),
                "question_score": tag.get("question_score", 0)
            })
        
        return tags
    
    def _get_top_answers(self, user_id: int, page_size: int = 10) -> Dict[str, Any]:
        """Get user's top answers."""
        data = self._make_request(
            f"users/{user_id}/answers",
            {
                "order": "desc",
                "sort": "votes",
                "pagesize": page_size,
                "filter": "!9_bDDxJY5"
            }
        )
        
        answers = []
        total_score = 0
        accepted_count = 0
        
        for answer in data.get("items", []):
            score = answer.get("score", 0)
            is_accepted = answer.get("is_accepted", False)
            
            total_score += score
            if is_accepted:
                accepted_count += 1
            
            answers.append({
                "answer_id": answer.get("answer_id"),
                "question_id": answer.get("question_id"),
                "score": score,
                "is_accepted": is_accepted,
                "creation_date": self._format_timestamp(answer.get("creation_date")),
                "link": answer.get("link"),
                "title": answer.get("title", "")
            })
        
        return {
            "total": data.get("total", 0),
            "total_score": total_score,
            "accepted_count": accepted_count,
            "top_answers": answers
        }
    
    def _get_questions(self, user_id: int, page_size: int = 10) -> Dict[str, Any]:
        """Get user's questions."""
        data = self._make_request(
            f"users/{user_id}/questions",
            {
                "order": "desc",
                "sort": "votes",
                "pagesize": page_size,
                "filter": "!9_bDDxJY5"
            }
        )
        
        questions = []
        total_score = 0
        
        for question in data.get("items", []):
            score = question.get("score", 0)
            total_score += score
            
            questions.append({
                "question_id": question.get("question_id"),
                "title": question.get("title"),
                "score": score,
                "answer_count": question.get("answer_count", 0),
                "view_count": question.get("view_count", 0),
                "is_answered": question.get("is_answered", False),
                "creation_date": self._format_timestamp(question.get("creation_date")),
                "link": question.get("link"),
                "tags": question.get("tags", [])
            })
        
        return {
            "total": data.get("total", 0),
            "total_score": total_score,
            "top_questions": questions
        }
    
    def _format_timestamp(self, timestamp: Optional[int]) -> Optional[str]:
        """Convert Unix timestamp to ISO format."""
        if timestamp:
            return datetime.fromtimestamp(timestamp).isoformat()
        return None
    
    def _calculate_account_age(self, creation_timestamp: Optional[int]) -> int:
        """Calculate account age in days."""
        if creation_timestamp:
            creation_date = datetime.fromtimestamp(creation_timestamp)
            age = datetime.now() - creation_date
            return age.days
        return 0
    
    def check_quota(self) -> Dict[str, Any]:
        """Check API quota remaining."""
        data = self._make_request("info")
        
        if "quota_remaining" in data:
            return {
                "quota_remaining": data.get("quota_remaining"),
                "quota_max": data.get("quota_max")
            }
        
        return {"error": "Unable to check quota"}
