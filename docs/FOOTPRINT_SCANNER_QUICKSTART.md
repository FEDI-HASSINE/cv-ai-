# 🚀 Footprint Scanner - Quick Start

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for LinkedIn scraping)
playwright install chromium
```

## Quick Start - CLI

```bash
# Analyze GitHub profile
python scripts/footprint_cli.py --github torvalds --out ./reports

# Analyze multiple platforms
python scripts/footprint_cli.py \
  --github octocat \
  --so 123456 \
  --out ./reports
```

## Quick Start - Python

```python
from src.core.footprint_scanner import FootprintScanner

# Initialize
scanner = FootprintScanner(github_token="ghp_your_token")

# Analyze
analysis = scanner.analyze_footprint(
    github_username="torvalds",
    export_text="./reports/footprint.txt",
    export_json="./reports/footprint.json"
)

# Get summary
summary = scanner.get_summary(analysis)
print(f"Overall Score: {summary['overall_score']}/100")
```

## Configuration

1. Copy `.env.example` to `.env`
2. Add your API credentials:
   - `GITHUB_TOKEN` - Get from https://github.com/settings/tokens
   - `STACKOVERFLOW_KEY` - Register at https://stackapps.com

## Documentation

📚 **Full documentation**: [docs/FOOTPRINT_SCANNER.md](docs/FOOTPRINT_SCANNER.md)

Covers:
- Complete feature list
- Installation guide
- Configuration options
- API reference
- Ethical guidelines
- Troubleshooting

## Examples

- JSON sample: `examples/footprint_report_sample.json`
- CLI usage: See `docs/FOOTPRINT_SCANNER.md`

## Testing

```bash
# Run tests
pytest tests/test_footprint_scanner.py -v

# With coverage
pytest tests/test_footprint_scanner.py --cov=src.core --cov-report=html
```

## Features

✅ GitHub API integration (repos, stars, languages, activity)  
✅ StackOverflow API integration (reputation, badges, answers)  
✅ LinkedIn scraping with Crawlee (requires consent)  
✅ Intelligent scoring system (0-100 scale)  
✅ Personalized insights and recommendations  
✅ 30-day action plan for improvement  
✅ Export to TXT and JSON formats  
✅ CLI and Python API  
✅ Comprehensive tests  

## Architecture

```
src/core/
├── footprint_scanner.py       # Main orchestrator
├── scoring_engine.py           # Score calculation
├── insights_generator.py       # Insights & recommendations
├── collectors/
│   ├── github_collector.py     # GitHub API
│   ├── stackoverflow_collector.py  # StackOverflow API
│   └── linkedin_scraper.py     # Crawlee scraper
└── exporters/
    ├── text_exporter.py        # TXT reports
    └── json_exporter.py        # JSON reports
```

## Ethical Usage ⚖️

**IMPORTANT**: LinkedIn scraping requires:
- ✅ Explicit user consent
- ✅ Only for personal profiles or with permission
- ❌ Never for unauthorized data collection

See [docs/FOOTPRINT_SCANNER.md#ethical-guidelines](docs/FOOTPRINT_SCANNER.md#ethical-guidelines)

## License

Part of CV-AI project. See main README for details.
