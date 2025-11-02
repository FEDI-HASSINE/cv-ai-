"""
GitHub Data Collector
Uses GitHub API to collect user activity, repositories, and statistics.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class GitHubCollector:
    """
    Collects data from GitHub API with rate limiting and retry logic.
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub collector.
        
        Args:
            token: GitHub Personal Access Token (optional but recommended)
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
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
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "cv-ai-footprint-scanner/1.0"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        session.headers.update(headers)
        return session
    
    def collect(self, username: str) -> Dict[str, Any]:
        """
        Collect comprehensive GitHub data for a user.
        
        Args:
            username: GitHub username
            
        Returns:
            Dictionary containing GitHub profile data and statistics
        """
        try:
            logger.info(f"Collecting GitHub data for user: {username}")
            
            # Get user profile
            user_data = self._get_user_info(username)
            if not user_data:
                return {"error": "User not found", "success": False}
            
            # Get repositories
            repos_data = self._get_repositories(username)
            
            # Get contribution stats
            contribution_stats = self._analyze_contributions(username)
            
            # Get language statistics
            language_stats = self._get_language_stats(repos_data)
            
            # Calculate metrics
            metrics = self._calculate_metrics(user_data, repos_data)
            
            result = {
                "success": True,
                "username": username,
                "profile": {
                    "name": user_data.get("name"),
                    "bio": user_data.get("bio"),
                    "company": user_data.get("company"),
                    "location": user_data.get("location"),
                    "email": user_data.get("email"),
                    "blog": user_data.get("blog"),
                    "twitter": user_data.get("twitter_username"),
                    "avatar_url": user_data.get("avatar_url"),
                    "created_at": user_data.get("created_at"),
                    "updated_at": user_data.get("updated_at")
                },
                "statistics": {
                    "public_repos": user_data.get("public_repos", 0),
                    "public_gists": user_data.get("public_gists", 0),
                    "followers": user_data.get("followers", 0),
                    "following": user_data.get("following", 0),
                    "total_stars": metrics["total_stars"],
                    "total_forks": metrics["total_forks"],
                    "total_watchers": metrics["total_watchers"]
                },
                "repositories": {
                    "total": len(repos_data),
                    "top_repos": self._get_top_repositories(repos_data, limit=5),
                    "recent_activity": self._get_recent_activity(repos_data, days=30)
                },
                "languages": language_stats,
                "contributions": contribution_stats,
                "collected_at": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully collected GitHub data for {username}")
            return result
            
        except Exception as e:
            logger.error(f"Error collecting GitHub data for {username}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "username": username
            }
    
    def _get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user profile information."""
        try:
            response = self.session.get(f"{self.BASE_URL}/users/{username}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching user info: {str(e)}")
            return None
    
    def _get_repositories(self, username: str, max_repos: int = 100) -> List[Dict[str, Any]]:
        """Get user's public repositories."""
        repos = []
        page = 1
        per_page = 100
        
        try:
            while len(repos) < max_repos:
                response = self.session.get(
                    f"{self.BASE_URL}/users/{username}/repos",
                    params={
                        "sort": "updated",
                        "per_page": per_page,
                        "page": page
                    }
                )
                response.raise_for_status()
                
                batch = response.json()
                if not batch:
                    break
                
                repos.extend(batch)
                
                if len(batch) < per_page:
                    break
                
                page += 1
            
            return repos[:max_repos]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching repositories: {str(e)}")
            return []
    
    def _analyze_contributions(self, username: str) -> Dict[str, Any]:
        """Analyze user contributions (simplified version)."""
        # Note: Full contribution data requires scraping or GraphQL API
        # This is a simplified version using available data
        return {
            "note": "Full contribution calendar requires GitHub GraphQL API",
            "data_source": "repository activity"
        }
    
    def _get_language_stats(self, repos: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate language statistics from repositories."""
        languages = {}
        
        for repo in repos:
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        # Sort by count
        sorted_languages = dict(
            sorted(languages.items(), key=lambda x: x[1], reverse=True)
        )
        
        return sorted_languages
    
    def _calculate_metrics(self, user_data: Dict[str, Any], repos: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate various GitHub metrics."""
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
        total_forks = sum(repo.get("forks_count", 0) for repo in repos)
        total_watchers = sum(repo.get("watchers_count", 0) for repo in repos)
        
        return {
            "total_stars": total_stars,
            "total_forks": total_forks,
            "total_watchers": total_watchers
        }
    
    def _get_top_repositories(self, repos: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """Get top repositories by stars."""
        sorted_repos = sorted(
            repos,
            key=lambda r: r.get("stargazers_count", 0),
            reverse=True
        )
        
        top_repos = []
        for repo in sorted_repos[:limit]:
            top_repos.append({
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "url": repo.get("html_url"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "language": repo.get("language"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at")
            })
        
        return top_repos
    
    def _get_recent_activity(self, repos: List[Dict[str, Any]], days: int = 30) -> Dict[str, Any]:
        """Analyze recent repository activity."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        recent_repos = [
            repo for repo in repos
            if datetime.fromisoformat(repo.get("updated_at", "2000-01-01T00:00:00Z").replace("Z", "+00:00")) > cutoff_date
        ]
        
        return {
            "repos_updated": len(recent_repos),
            "period_days": days,
            "repos": [
                {
                    "name": repo.get("name"),
                    "updated_at": repo.get("updated_at")
                }
                for repo in recent_repos[:10]
            ]
        }
    
    def check_rate_limit(self) -> Dict[str, Any]:
        """Check current rate limit status."""
        try:
            response = self.session.get(f"{self.BASE_URL}/rate_limit")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            return {"error": str(e)}
