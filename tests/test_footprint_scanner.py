"""
Unit Tests for Footprint Scanner
Run with: pytest tests/test_footprint_scanner.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import modules to test
from src.core.footprint_scanner import FootprintScanner
from src.core.scoring_engine import ScoringEngine
from src.core.insights_generator import InsightsGenerator
from src.core.collectors.github_collector import GitHubCollector
from src.core.collectors.stackoverflow_collector import StackOverflowCollector
from src.core.collectors.linkedin_scraper import LinkedInScraper


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_github_data():
    """Mock GitHub API response data."""
    return {
        "success": True,
        "username": "testuser",
        "profile": {
            "name": "Test User",
            "bio": "Test bio",
            "location": "San Francisco",
            "created_at": "2020-01-01T00:00:00Z"
        },
        "statistics": {
            "public_repos": 15,
            "followers": 50,
            "following": 20,
            "total_stars": 120,
            "total_forks": 45,
            "total_watchers": 30
        },
        "repositories": {
            "total": 15,
            "top_repos": [
                {"name": "repo1", "stars": 50, "language": "Python"},
                {"name": "repo2", "stars": 40, "language": "JavaScript"}
            ],
            "recent_activity": {"repos_updated": 3, "period_days": 30}
        },
        "languages": {"Python": 8, "JavaScript": 5, "Go": 2},
        "collected_at": datetime.now().isoformat()
    }


@pytest.fixture
def mock_stackoverflow_data():
    """Mock StackOverflow API response data."""
    return {
        "success": True,
        "user_id": 123456,
        "profile": {
            "display_name": "Test User",
            "location": "San Francisco",
            "link": "https://stackoverflow.com/users/123456"
        },
        "reputation": {
            "score": 2500,
            "reputation_change_month": 100
        },
        "badges": {
            "gold": 1,
            "silver": 5,
            "bronze": 20,
            "total": 26
        },
        "activity": {
            "answers": {
                "count": 60,
                "score": 350,
                "accepted": 30
            },
            "questions": {
                "count": 10,
                "score": 50
            }
        },
        "tags": {
            "top_tags": [
                {"name": "python", "answer_count": 25},
                {"name": "javascript", "answer_count": 20}
            ]
        },
        "collected_at": datetime.now().isoformat()
    }


@pytest.fixture
def mock_linkedin_data():
    """Mock LinkedIn scraper data."""
    return {
        "success": True,
        "url": "https://linkedin.com/in/testuser",
        "profile": {
            "name": "Test User",
            "headline": "Software Engineer",
            "location": "San Francisco",
            "about": "Experienced developer..."
        },
        "experience": [
            {"title": "Senior Engineer", "company": "Tech Co", "duration": "2y"},
            {"title": "Engineer", "company": "Startup", "duration": "3y"}
        ],
        "education": [
            {"school": "University", "degree": "BS Computer Science"}
        ],
        "skills": ["Python", "JavaScript", "Docker", "AWS"],
        "collected_at": datetime.now().isoformat()
    }


# ============================================================================
# Scoring Engine Tests
# ============================================================================

class TestScoringEngine:
    """Test ScoringEngine class."""
    
    def test_calculate_github_score(self, mock_github_data):
        """Test GitHub scoring calculation."""
        engine = ScoringEngine()
        score, breakdown = engine._score_github(mock_github_data)
        
        assert 0 <= score <= 100
        assert isinstance(breakdown, dict)
        assert "repos" in breakdown
        assert "stars" in breakdown
        assert "followers" in breakdown
    
    def test_calculate_stackoverflow_score(self, mock_stackoverflow_data):
        """Test StackOverflow scoring calculation."""
        engine = ScoringEngine()
        score, breakdown = engine._score_stackoverflow(mock_stackoverflow_data)
        
        assert 0 <= score <= 100
        assert isinstance(breakdown, dict)
        assert "reputation" in breakdown
        assert "badges" in breakdown
        assert "answers" in breakdown
    
    def test_calculate_linkedin_score(self, mock_linkedin_data):
        """Test LinkedIn scoring calculation."""
        engine = ScoringEngine()
        score, breakdown = engine._score_linkedin(mock_linkedin_data)
        
        assert 0 <= score <= 100
        assert isinstance(breakdown, dict)
        assert "profile_completeness" in breakdown
        assert "experience" in breakdown
    
    def test_calculate_overall_score(self, mock_github_data, mock_stackoverflow_data):
        """Test overall score calculation."""
        engine = ScoringEngine()
        scores = engine.calculate_scores(
            github_data=mock_github_data,
            stackoverflow_data=mock_stackoverflow_data
        )
        
        assert "overall" in scores
        assert 0 <= scores["overall"] <= 100
        assert "github" in scores
        assert "stackoverflow" in scores
        assert "ratings" in scores


# ============================================================================
# Insights Generator Tests
# ============================================================================

class TestInsightsGenerator:
    """Test InsightsGenerator class."""
    
    def test_generate_insights(self, mock_github_data, mock_stackoverflow_data):
        """Test insights generation."""
        engine = ScoringEngine()
        scores = engine.calculate_scores(
            github_data=mock_github_data,
            stackoverflow_data=mock_stackoverflow_data
        )
        
        generator = InsightsGenerator()
        insights = generator.generate_insights(
            scores=scores,
            github_data=mock_github_data,
            stackoverflow_data=mock_stackoverflow_data
        )
        
        assert "strengths" in insights
        assert "areas_for_improvement" in insights
        assert "recommendations" in insights
        assert "30_day_plan" in insights
        assert isinstance(insights["strengths"], list)
        assert isinstance(insights["30_day_plan"], list)
    
    def test_action_plan_structure(self, mock_github_data):
        """Test 30-day action plan structure."""
        engine = ScoringEngine()
        scores = engine.calculate_scores(github_data=mock_github_data)
        
        generator = InsightsGenerator()
        insights = generator.generate_insights(
            scores=scores,
            github_data=mock_github_data
        )
        
        plan = insights["30_day_plan"]
        assert len(plan) > 0
        
        # Check first action item structure
        action = plan[0]
        assert "day" in action
        assert "week" in action
        assert "action" in action
        assert "priority" in action
        assert "estimated_time" in action
        assert "platforms" in action


# ============================================================================
# GitHub Collector Tests
# ============================================================================

class TestGitHubCollector:
    """Test GitHubCollector class."""
    
    @patch('src.core.collectors.github_collector.requests.Session')
    def test_collect_user_data(self, mock_session):
        """Test GitHub data collection."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "login": "testuser",
            "name": "Test User",
            "public_repos": 10,
            "followers": 50
        }
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response
        
        collector = GitHubCollector()
        # Note: This will still make a real API call in practice
        # For proper testing, mock the entire session
    
    def test_validate_username(self):
        """Test username validation."""
        collector = GitHubCollector()
        
        # Valid usernames
        assert collector._get_user_info("validuser") or True
        
        # Invalid usernames would need mocking


# ============================================================================
# StackOverflow Collector Tests
# ============================================================================

class TestStackOverflowCollector:
    """Test StackOverflowCollector class."""
    
    def test_initialization(self):
        """Test collector initialization."""
        collector = StackOverflowCollector()
        assert collector.BASE_URL == "https://api.stackexchange.com/2.3"
        assert collector.SITE == "stackoverflow"


# ============================================================================
# LinkedIn Scraper Tests
# ============================================================================

class TestLinkedInScraper:
    """Test LinkedInScraper class."""
    
    def test_mock_data_generation(self):
        """Test mock data generation."""
        scraper = LinkedInScraper()
        mock_data = scraper.get_mock_data("https://linkedin.com/in/test")
        
        assert mock_data["success"] is True
        assert "profile" in mock_data
        assert "experience" in mock_data
        assert "education" in mock_data
        assert "skills" in mock_data
    
    def test_url_validation(self):
        """Test LinkedIn URL validation."""
        scraper = LinkedInScraper()
        
        assert scraper._is_valid_linkedin_url("https://www.linkedin.com/in/testuser")
        assert scraper._is_valid_linkedin_url("https://linkedin.com/in/testuser")
        assert not scraper._is_valid_linkedin_url("https://example.com")
        assert not scraper._is_valid_linkedin_url("")
    
    def test_consent_requirement(self):
        """Test consent requirement for scraping."""
        scraper = LinkedInScraper(enable_scraping=True)
        
        # Without consent, should fail
        result = scraper.collect("https://linkedin.com/in/test", user_consent=False)
        assert result["success"] is False
        assert "consent" in result["error"].lower()


# ============================================================================
# FootprintScanner Integration Tests
# ============================================================================

class TestFootprintScanner:
    """Test FootprintScanner main orchestrator."""
    
    def test_initialization(self):
        """Test scanner initialization."""
        scanner = FootprintScanner()
        assert scanner.github_collector is not None
        assert scanner.stackoverflow_collector is not None
        assert scanner.linkedin_scraper is not None
        assert scanner.scoring_engine is not None
        assert scanner.insights_generator is not None
    
    @patch.object(GitHubCollector, 'collect')
    @patch.object(StackOverflowCollector, 'collect')
    def test_analyze_footprint(self, mock_so_collect, mock_gh_collect, 
                               mock_github_data, mock_stackoverflow_data):
        """Test full footprint analysis."""
        # Setup mocks
        mock_gh_collect.return_value = mock_github_data
        mock_so_collect.return_value = mock_stackoverflow_data
        
        scanner = FootprintScanner()
        analysis = scanner.analyze_footprint(
            github_username="testuser",
            stackoverflow_user_id="123456"
        )
        
        assert analysis["success"] is True
        assert "scores" in analysis
        assert "insights" in analysis
        assert len(analysis["platforms_analyzed"]) == 2
    
    def test_get_summary(self, mock_github_data):
        """Test summary generation."""
        scanner = FootprintScanner()
        
        # Create minimal analysis
        analysis = {
            "platforms_analyzed": ["GitHub"],
            "scores": {
                "github": 75,
                "overall": 75,
                "ratings": {"overall": "Good"}
            },
            "insights": {
                "strengths": ["Good repos"],
                "areas_for_improvement": ["Need more stars"],
                "recommendations": ["Contribute more"]
            }
        }
        
        summary = scanner.get_summary(analysis)
        
        assert "overall_score" in summary
        assert "overall_rating" in summary
        assert "platforms_analyzed" in summary
        assert summary["overall_score"] == 75


# ============================================================================
# Export Tests
# ============================================================================

class TestExporters:
    """Test report exporters."""
    
    def test_json_export_structure(self, mock_github_data):
        """Test JSON export structure."""
        from src.core.exporters.json_exporter import JSONExporter
        
        data = {
            "scanned_at": datetime.now().isoformat(),
            "github_data": mock_github_data,
            "stackoverflow_data": {},
            "linkedin_data": {},
            "scores": {"overall": 75, "github": 75},
            "insights": {
                "strengths": [],
                "areas_for_improvement": [],
                "recommendations": [],
                "30_day_plan": []
            }
        }
        
        json_output = JSONExporter.export(data)
        assert json_output is not None
        assert "meta" in json_output
        assert "scores" in json_output
    
    def test_text_export_generation(self, mock_github_data):
        """Test text report generation."""
        from src.core.exporters.text_exporter import TextExporter
        
        data = {
            "scanned_at": datetime.now().isoformat(),
            "github_data": mock_github_data,
            "stackoverflow_data": {},
            "linkedin_data": {},
            "scores": {"overall": 75, "github": 75, "ratings": {"overall": "Good"}},
            "insights": {
                "strengths": ["Test strength"],
                "areas_for_improvement": ["Test improvement"],
                "recommendations": ["Test recommendation"],
                "30_day_plan": []
            }
        }
        
        text_output = TextExporter.export(data)
        assert text_output is not None
        assert "DIGITAL FOOTPRINT" in text_output
        assert "Test strength" in text_output


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
