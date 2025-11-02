# Footprint Scanner - Complete Guide

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [API Reference](#api-reference)
7. [Ethical Guidelines](#ethical-guidelines)
8. [Limitations](#limitations)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The **Footprint Scanner** analyzes your professional digital presence across LinkedIn, GitHub, and StackOverflow. It provides:

- Comprehensive data collection from multiple platforms
- Intelligent scoring system (0-100 scale)
- Personalized insights and recommendations
- 30-day action plan for improvement
- Exportable reports (TXT and JSON formats)

---

## ✨ Features

### Platform Support

#### GitHub Analysis
- **Data Collected**: Public repositories, stars, forks, followers, languages, contribution activity
- **Method**: GitHub REST API
- **Requirements**: Optional API token (highly recommended for higher rate limits)

#### StackOverflow Analysis
- **Data Collected**: Reputation, badges, top answers, questions, tags, activity statistics
- **Method**: Stack Exchange API
- **Requirements**: Optional API key (recommended for higher quotas)

#### LinkedIn Analysis
- **Data Collected**: Profile info, experience, education, skills
- **Method**: Web scraping with Crawlee + Playwright (requires explicit consent)
- **Requirements**: User consent, scraping enabled

### Scoring System

Each platform scored 0-100 based on:
- **GitHub**: Repos (20%), Stars (25%), Followers (20%), Activity (20%), Languages (15%)
- **StackOverflow**: Reputation (30%), Badges (25%), Answers (25%), Questions (10%), Tags (10%)
- **LinkedIn**: Profile completeness (30%), Experience (30%), Education (20%), Skills (20%)

Overall score: Weighted average (GitHub: 35%, StackOverflow: 35%, LinkedIn: 30%)

### Insights & Recommendations

- Platform-specific strengths and improvements
- Actionable recommendations prioritized by impact
- 30-day action plan with weekly goals
- Time estimates and priority levels

---

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Optional: Docker (for devcontainer environment)

### Install Dependencies

```bash
# Navigate to project root
cd /workspaces/cv-ai-

# Install requirements
pip install -r requirements.txt

# Install Playwright browsers (required for LinkedIn scraping)
playwright install chromium
```

### Verify Installation

```bash
# Test CLI
python scripts/footprint_cli.py --version

# Test imports
python -c "from src.core.footprint_scanner import FootprintScanner; print('OK')"
```

---

## ⚙️ Configuration

### 1. Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
# GitHub Token (optional but recommended)
GITHUB_TOKEN=ghp_your_token_here

# StackOverflow Key (optional)
STACKOVERFLOW_KEY=your_key_here

# Enable LinkedIn scraping (default: false)
ENABLE_SCRAPING=false

# Require user consent (default: true)
REQUIRE_CONSENT=true
```

### 2. Get API Credentials

#### GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `public_repo`, `read:user`
4. Copy token to `.env` file

**Benefits**: Increases rate limit from 60 to 5,000 requests/hour

#### StackOverflow API Key

1. Go to https://stackapps.com/apps/oauth/register
2. Fill in application details
3. Copy API key to `.env` file

**Benefits**: Increases quota from 300 to 10,000 requests/day

---

## 📖 Usage

### Command Line Interface (CLI)

#### Basic Usage

```bash
# Analyze GitHub profile
python scripts/footprint_cli.py --github torvalds --out ./reports

# Analyze multiple platforms
python scripts/footprint_cli.py \
  --github octocat \
  --so 123456 \
  --linkedin https://linkedin.com/in/username \
  --out ./reports

# With API credentials
python scripts/footprint_cli.py \
  --github username \
  --github-token ghp_your_token \
  --out ./reports
```

#### Advanced Options

```bash
# Enable LinkedIn scraping (requires consent)
python scripts/footprint_cli.py \
  --linkedin https://linkedin.com/in/user \
  --enable-scraping \
  --linkedin-consent

# Export specific format
python scripts/footprint_cli.py \
  --github user \
  --format json \
  --out ./reports

# Verbose output
python scripts/footprint_cli.py \
  --github user \
  --verbose
```

### Python API

#### Basic Example

```python
from src.core.footprint_scanner import FootprintScanner

# Initialize scanner
scanner = FootprintScanner(
    github_token="ghp_your_token",
    stackoverflow_key="your_key"
)

# Run analysis
analysis = scanner.analyze_footprint(
    github_username="torvalds",
    stackoverflow_user_id="123456",
    export_text="./reports/footprint.txt",
    export_json="./reports/footprint.json"
)

# Get summary
summary = scanner.get_summary(analysis)
print(f"Overall Score: {summary['overall_score']}/100")
print(f"Rating: {summary['overall_rating']}")
```

#### Advanced Example

```python
from src.core.footprint_scanner import FootprintScanner

# Initialize with LinkedIn scraping enabled
scanner = FootprintScanner(
    github_token="ghp_token",
    enable_linkedin_scraping=True
)

# Analyze with consent
analysis = scanner.analyze_footprint(
    github_username="octocat",
    linkedin_url="https://linkedin.com/in/user",
    linkedin_consent=True,  # ⚠️ Only with explicit user consent
    stackoverflow_user_id="123456"
)

# Access detailed data
if analysis['success']:
    github_data = analysis['github_data']
    scores = analysis['scores']
    insights = analysis['insights']
    
    # Print top repositories
    for repo in github_data['repositories']['top_repos'][:3]:
        print(f"{repo['name']}: {repo['stars']} stars")
    
    # Print action plan
    for action in insights['30_day_plan'][:5]:
        print(f"Day {action['day']}: {action['action']}")
```

### Streamlit Integration

The Footprint Scanner is integrated into the Streamlit app at `pages/4_🌐_Footprint_Scanner.py`. Use the web interface for interactive analysis.

---

## 📚 API Reference

### FootprintScanner Class

#### Constructor

```python
FootprintScanner(
    github_token: Optional[str] = None,
    stackoverflow_key: Optional[str] = None,
    enable_linkedin_scraping: bool = False
)
```

#### Methods

##### `analyze_footprint()`

```python
analyze_footprint(
    linkedin_url: Optional[str] = None,
    github_username: Optional[str] = None,
    stackoverflow_user_id: Optional[str] = None,
    linkedin_consent: bool = False,
    export_text: Optional[str] = None,
    export_json: Optional[str] = None
) -> Dict[str, Any]
```

Returns:
```python
{
    "scanned_at": "2024-11-02T10:30:00",
    "platforms_analyzed": ["GitHub", "StackOverflow"],
    "github_data": {...},
    "stackoverflow_data": {...},
    "linkedin_data": {...},
    "scores": {
        "github": 75,
        "stackoverflow": 68,
        "linkedin": 0,
        "overall": 72,
        "ratings": {...},
        "breakdown": {...}
    },
    "insights": {
        "strengths": [...],
        "areas_for_improvement": [...],
        "recommendations": [...],
        "30_day_plan": [...]
    },
    "success": True
}
```

##### `get_summary()`

```python
get_summary(analysis: Dict[str, Any]) -> Dict[str, Any]
```

Returns simplified summary of results.

##### `export_report()`

```python
export_report(
    analysis: Dict[str, Any],
    format: str = "text",
    output_path: Optional[str] = None
) -> str
```

---

## ⚖️ Ethical Guidelines

### CRITICAL: User Consent

**LinkedIn Scraping**:
- ✅ ONLY with explicit user consent
- ✅ ONLY for the user's own profile or with written permission
- ❌ NEVER for unauthorized data collection
- ❌ NEVER for commercial scraping without LinkedIn approval

### Best Practices

1. **Transparency**: Always inform users what data is collected
2. **Purpose Limitation**: Use data only for stated purpose (career analysis)
3. **Data Minimization**: Collect only necessary information
4. **Security**: Never store credentials or tokens in code
5. **Respect ToS**: Follow all platform Terms of Service

### Rate Limiting

- GitHub: Max 5,000 requests/hour (with token)
- StackOverflow: Max 10,000 requests/day (with key)
- LinkedIn: Manual rate limiting implemented (0.5 req/sec)

### robots.txt Compliance

All scrapers respect `robots.txt` directives. LinkedIn scraping:
- Uses headless browser to mimic normal browsing
- Includes proper User-Agent identification
- Implements backoff on errors

---

## ⚠️ Limitations

### Platform-Specific

**GitHub**:
- Only public repositories analyzed
- Contribution graph requires GraphQL API (not implemented)
- Private organizations not visible

**StackOverflow**:
- Only public profile data
- Some metrics require authentication
- API quota limits apply

**LinkedIn**:
- Scraping unreliable due to login walls
- Public profiles only
- May break if LinkedIn changes page structure
- Consider using LinkedIn Data Export instead

### Technical Limitations

1. **No Real-Time Updates**: Data is point-in-time snapshot
2. **API Dependencies**: Subject to API changes and outages
3. **Network Requirements**: Requires internet connectivity
4. **Resource Intensive**: LinkedIn scraping uses headless browser

---

## 🔧 Troubleshooting

### Common Issues

#### "Rate limit exceeded" (GitHub)

**Solution**: Add GitHub token to `.env`:
```bash
GITHUB_TOKEN=ghp_your_token_here
```

#### "Quota exceeded" (StackOverflow)

**Solution**: Add API key or wait 24 hours for quota reset

#### "Login required" (LinkedIn)

**Cause**: LinkedIn shows login wall for some profiles

**Solutions**:
1. Use LinkedIn Data Export (recommended)
2. Ensure profile is set to public
3. Use mock data for testing

#### "Module not found" errors

**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

#### Playwright browser not found

**Solution**: Install Playwright browsers:
```bash
playwright install chromium
```

### Debug Mode

Enable verbose logging:

```bash
# CLI
python scripts/footprint_cli.py --github user --verbose

# Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. Check logs in `./logs/` directory
2. Review error messages carefully
3. Verify API credentials are correct
4. Test with known-good usernames (e.g., `torvalds` on GitHub)
5. Open an issue on GitHub with logs

---

## 📊 Output Examples

### Text Report

```
================================================================================
DIGITAL FOOTPRINT ANALYSIS REPORT
================================================================================
Generated: 2024-11-02 10:30:00

Target Profiles:
  • GitHub: torvalds
  • StackOverflow: Jon Skeet (ID: 22656)

--------------------------------------------------------------------------------
OVERALL SCORES
--------------------------------------------------------------------------------

Overall Score: 85/100 - Very Good

Platform Scores:
  GitHub           88/100  [████████████████████]  Very Good
  StackOverflow    82/100  [████████████████░░░░]  Very Good

[... full report content ...]
```

### JSON Report

```json
{
  "meta": {
    "scanned_at": "2024-11-02T10:30:00",
    "target": {
      "github": "torvalds",
      "stackoverflow": "22656"
    },
    "platforms_analyzed": ["GitHub", "StackOverflow"]
  },
  "scores": {
    "github": 88,
    "stackoverflow": 82,
    "overall": 85
  },
  "30_day_plan": [
    {
      "day": 1,
      "action": "Audit all profiles",
      "priority": "high"
    }
  ]
}
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Follow ethical guidelines
2. Add tests for new features
3. Update documentation
4. Respect API rate limits in tests

---

## 📄 License

Part of CV-AI project. See main README for license information.

---

## 📞 Contact

For questions, issues, or suggestions:
- Open an issue on GitHub
- Check project documentation
- Review troubleshooting section

**Last Updated**: November 2, 2024
