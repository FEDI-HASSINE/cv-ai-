# UtopiaHire - AI Career Architect 💼

> **Empowering careers in MENA & Sub-Saharan Africa through AI-powered career development tools**

[![Made with Streamlit](https://img.shields.io/badge/Made%20with-Streamlit-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Overview

**UtopiaHire** is a comprehensive AI-powered career development platform designed specifically for job seekers in MENA (Middle East & North Africa) and Sub-Saharan Africa regions. The platform combines advanced NLP techniques with intelligent matching algorithms to help candidates optimize their resumes and discover relevant opportunities.

### Key Features

- **📄 Resume Reviewer**: AI-powered analysis with ATS scoring, skill extraction, and comprehensive insights
  - Download detailed analysis reports (Text + JSON)
  - ATS compatibility scoring
  - Skills extraction and categorization
  - Strengths and weaknesses identification
  
- **✍️ Resume Rewriter**: Smart suggestions to optimize resume content, language, and formatting
  - Download rewriting recommendations (Text + JSON)
  - Action verb suggestions by category
  - Weak phrase detection and alternatives
  - Quantification opportunities
  
- **🎯 Job Matcher**: Regional job recommendations with **DYNAMIC REAL-TIME JOB SEARCH** 🔥
  - **NEW: Search real jobs from LinkedIn, Indeed, Glassdoor, Google Jobs**
  - **NEW: Professional jobs table with sortable columns & direct links**
  - **NEW: Detailed match analysis with visual progress bars**
  - **NEW: Personalized enhancement suggestions (High/Medium/Low priority)**
  - **NEW: Application readiness score (Ready/Improve/Prepare)**
  - **NEW: CSV export for job tracking**
  - **Direct application links to live job postings**
  - Download job matches report (Text + JSON)
  - Smart matching algorithm (60% skills, 30% experience, 10% location)
  - Regional filtering (MENA, Sub-Saharan Africa, North Africa, Global)
  - Missing skills identification with learning recommendations
  - Sample database mode for demos
  
- **🌐 Footprint Scanner**: Analyze professional presence across LinkedIn, GitHub, and StackOverflow
  - Download footprint analysis (Text + JSON)
  - Multi-platform digital presence scoring
  - Platform-specific recommendations
  - 30-day action plan

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/FEDI-HASSINE/cv-ai-.git
cd cv-ai-
```

2. **Create and activate virtual environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate on Linux/Mac
source venv/bin/activate

# Activate on Windows
# venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application (Streamlit UI)**
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Alternative run modes

- Streamlit with helper script
  ```bash
  ./setup.sh && ./run.sh
  ```
- FastAPI backend (REST API)
  ```bash
  uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
  # Docs: http://localhost:8000/api/docs
  ```
- Footprint Scanner CLI
  ```bash
  python scripts/footprint_cli.py --github octocat --out ./reports --format both
  ```

## 📁 Project Structure

```
cv-ai-/
├── app.py                      # Main Streamlit application
├── pages/                      # Multi-page app pages
│   ├── 1_📄_Resume_Reviewer.py
│   ├── 2_✍️_Resume_Rewriter.py
│   ├── 3_🎯_Job_Matcher.py
│   └── 4_🌐_Footprint_Scanner.py
├── src/                        # Core application logic
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── core/                  # Core modules
│   │   ├── resume_analyzer.py
│   │   ├── resume_rewriter.py
│   │   ├── job_matcher.py
│   │   └── footprint_scanner.py
│   └── utils/                 # Utility functions
│       ├── file_parser.py
│       └── helpers.py
├── data/                      # Data directory
├── temp/                      # Temporary files
├── models/                    # ML models (future)
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 🎯 Features in Detail

### 1. Resume Reviewer 📄

Upload your resume and get:
- **Overall quality score** (0-100)
- **ATS compatibility score** with keyword analysis
- **Skill extraction** (technical and soft skills)
- **Section detection** (Experience, Education, Skills, etc.)
- **Experience level estimation**
- **Strengths and weaknesses analysis**
- **Actionable improvement suggestions**
- **📥 Downloadable Reports**: Text and JSON formats with complete analysis

**Supported formats**: PDF, DOCX, DOC, TXT

### 2. Resume Rewriter ✍️

Optimize your resume with:
- **Weak phrase detection** and stronger alternatives
- **Action verb suggestions** by category
- **Quantification opportunities** for achievements
- **Formatting recommendations**
### 3. Job Matcher 🎯

Find relevant jobs with:
- **📊 Professional Jobs Table** with sortable columns and direct application links
- **📈 Detailed Match Analysis** with visual progress bars for skills, experience, and level
- **💡 Personalized Enhancement Suggestions** categorized by priority (High/Medium/Low)
- **🎯 Application Readiness Score** to know when you're ready to apply
- **📥 CSV Export** for job tracking in Excel/Google Sheets
- **Smart matching algorithm** (60% skills, 30% experience, 10% level)
- **Regional filtering** (MENA, Sub-Saharan Africa, North Africa, Global)
- **Industry and level filters**
- **Match percentage** for each job with color coding
- **Skill gap analysis** with specific learning recommendations
- **Skill development recommendations**
- **Regional market insights**
- **📥 Downloadable Reports**: Job matches and recommendations in Text and JSON
- **Match percentage** for each job
- **Skill gap analysis**
- **Skill development recommendations**
- **Regional market insights**
- **📥 Downloadable Reports**: Job matches and recommendations in Text and JSON

### 4. Footprint Scanner 🌐

Analyze your online presence:
- **LinkedIn profile analysis**
- **GitHub activity tracking**
- **StackOverflow reputation review**
- **Overall footprint score**
- **Platform-specific insights**
- **Personalized recommendations**
- **30-day improvement action plan**
- **📥 Downloadable Reports**: Complete footprint analysis in Text and JSON

## 🔧 Configuration

### Environment Variables (optional)

You can create a `.env` file to override defaults used by `src/config.py`.

```bash
touch .env
```

Common keys:
- `DEBUG` — Enable/disable debug mode (default: True)
- `API_BASE_URL` — Base URL for the API (default: http://localhost:8000/api/v1)
- `OPENAI_API_KEY` — If you want to use OpenAI in place of the default flows
- `GITHUB_TOKEN`, `STACKOVERFLOW_KEY` — For CLI footprint analysis (optional)

DeepSeek R1 via OpenRouter (used in the Resume Reviewer page) can be configured directly in the UI. Provide your OpenRouter API key in the sidebar when selecting “DeepSeek R1 (Recommandé)”.

### Customization

Edit `src/config.py` to customize:
- Supported file formats
- ATS keywords
- Regional settings
- Industry categories
- Job levels
- Skill databases

## 🏗️ Architecture

The application is built with a **modular, API-ready architecture**:

### Current Implementation
- **Frontend**: Streamlit for interactive UI
- **Backend Logic**: Python modules for core functionality
- **File Processing**: PDF and DOCX parsing
- **Analysis**: NLP-based text analysis and matching

### Backend API (included)

A FastAPI service is included in `src/api`. Start it with:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive docs: http://localhost:8000/api/docs

### Planned Architecture

```
Frontend (React/Streamlit)
         ↓
    API Gateway
         ↓
    ┌────┴────┐
    ↓         ↓
Backend API   Job Queue (Celery)
    ↓         ↓
Database  Cache (Redis)
```

## 🌍 Regional Focus

**Target Regions:**
- 🌙 **MENA** (Middle East & North Africa)
- 🌍 **Sub-Saharan Africa**
- 🇲🇦 **North Africa**
- 🌐 **Global** opportunities

**Regional Features:**
- Region-specific job recommendations
- Local skill demand analysis
- Market insights by region
- Cultural and language considerations

## 📊 Technology Stack

**Core Technologies:**
- Python 3.8+
- Streamlit (UI framework)
- PyPDF2 (PDF processing)
- python-docx (DOCX processing)

**Key Features:**
- 📥 Dual-format downloads (Text + JSON) for all reports
- 🎨 Professional UI with custom styling
- 🔄 Dynamic content analysis
- 📊 ATS scoring algorithm
- 🎯 Smart job matching
- 🌐 Multi-platform footprint scanning

**Future Integrations:**
- spaCy / Transformers (Advanced NLP)
- OpenAI API (LLM capabilities)
- Django/FastAPI (Backend API)
- PostgreSQL (Database)
- Redis (Caching)
- Docker (Containerization)

## 📥 Download Features

All modules support comprehensive report downloads:

- **Text Reports (.txt)**: Human-readable formatted reports perfect for sharing and printing
- **JSON Reports (.json)**: Structured data for programmatic use and API integration

See more in `docs/FOOTPRINT_SCANNER.md` and `docs/PROJECT_OVERVIEW.md`.

## 🔌 API quick reference

Base URL (local): `http://localhost:8000/api/v1`

- Health
  - `GET /health` — service status
  - `GET /ping` — simple ping
- Auth
  - `POST /auth/login` — returns `access_token` and `refresh_token` (demo: accepts any email with password length ≥ 8)
  - `POST /auth/refresh` — refreshes access token (use `Authorization: Bearer <refresh_token>`)
  - `GET /auth/me` — returns current user info (requires `Authorization: Bearer <access_token>`)
- Resume
  - `POST /resume/analyze` — analyze uploaded CV file (requires auth; accepts PDF/DOCX/DOC/TXT)
- Jobs
  - `POST /jobs/search` — live job search (keywords, region, level)
  - `POST /jobs/match` — semantic job matching for a candidate profile
  - `GET /jobs/regions` — available regions
  - `GET /jobs/industries` — available industries

Quick smoke test:

```bash
curl -s http://localhost:8000/api/v1/health | jq
```

## 🖥️ CLI: Footprint Scanner

Analyze digital presence from the terminal and export reports to `./reports`:

```bash
python scripts/footprint_cli.py --github octocat --out ./reports --format both
python scripts/footprint_cli.py --github torvalds --so 12345 --out ./reports
```

Optional environment variables:
- `GITHUB_TOKEN` — Higher rate limits for GitHub API
- `STACKOVERFLOW_KEY` — StackOverflow API key

LinkedIn scraping is disabled by default and requires explicit consent:

```bash
python scripts/footprint_cli.py --linkedin https://linkedin.com/in/your-profile \
  --enable-scraping --linkedin-consent --out ./reports
```

Note: If you plan to use Playwright-based scraping, you may need to install browsers once:

```bash
python -m playwright install
```

## 🧪 Tests

Run unit tests:

```bash
pytest -q
```

## 🤝 Contributing

This project is designed for the **IEEE TSYP13 Technical Challenge**. For contributions:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Project Context

**Built for**: IEEE TSYP13 Technical Challenge  
**Focus**: Regional employment challenges in Africa and MENA  
**Goal**: Empower job seekers with AI-powered career tools

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

<div align="center">

**🌍 Empowering careers across Africa and MENA regions**

Built with ❤️ using Python & Streamlit

[Report Bug](https://github.com/FEDI-HASSINE/cv-ai-/issues) · [Request Feature](https://github.com/FEDI-HASSINE/cv-ai-/issues)

</div>
