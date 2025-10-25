# UtopiaHire - Project Overview

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Project Structure](#project-structure)
7. [Modules](#modules)
8. [Future Enhancements](#future-enhancements)
9. [Contributing](#contributing)

---

## 1. Introduction

**UtopiaHire** is an AI-powered career development platform specifically designed for job seekers in MENA (Middle East & North Africa) and Sub-Saharan Africa regions. Built for the IEEE TSYP13 Technical Challenge, it addresses regional employment challenges through innovative AI solutions.

### Problem Statement

- High unemployment rates in MENA and Sub-Saharan Africa
- Limited access to career development tools
- Lack of regional job market insights
- Difficulty optimizing resumes for ATS systems
- Limited guidance on professional online presence

### Solution

UtopiaHire provides four core features:
1. **Resume Reviewer**: AI-powered analysis with ATS scoring
2. **Resume Rewriter**: Optimization suggestions
3. **Job Matcher**: Regional job recommendations
4. **Footprint Scanner**: Digital presence analysis

---

## 2. Features

### 2.1 Resume Reviewer 📄

**Capabilities:**
- Upload PDF, DOCX, DOC, or TXT files
- Extract contact information (email, phone, URLs)
- Detect resume sections (Experience, Education, Skills, etc.)
- Extract technical and soft skills (50+ technical skills, 15+ soft skills)
- Calculate ATS compatibility score
- Estimate years of experience
- Identify education level
- Analyze strengths and weaknesses
- Generate actionable suggestions

**Scoring Algorithm:**
- Overall Score (0-100):
  - 40% ATS Score
  - 30% Skills (technical + soft)
  - 20% Structure (sections)
  - 10% Contact Information

### 2.2 Resume Rewriter ✍️

**Capabilities:**
- Detect weak phrases and suggest alternatives
- Recommend action verbs by category (Leadership, Achievement, etc.)
- Identify quantification opportunities
- Suggest formatting improvements
- Provide content enhancement tips
- Show optimized section examples
- Priority-based recommendations (High/Medium/Low)

**Improvement Areas:**
- Language strength
- Quantifiable metrics
- Action verb diversity
- Formatting consistency
- Content optimization

### 2.3 Job Matcher 🎯

**Capabilities:**
- Manual profile input or resume upload
- Match jobs based on skills and experience
- Regional filtering (MENA, Sub-Saharan Africa, North Africa, Global)
- Industry and level filters
- Match percentage calculation
- Skill gap analysis
- Skill development recommendations
- Regional market insights

**Matching Algorithm:**
- 60% Skill Match (required + preferred)
- 30% Experience Match
- 10% Level Appropriateness

**Sample Job Database:**
- 10+ diverse job postings
- Multiple regions and industries
- Various seniority levels
- Remote and on-site options

### 2.4 Footprint Scanner 🌐

**Capabilities:**
- LinkedIn profile analysis
- GitHub activity tracking
- StackOverflow reputation review
- Overall footprint score (0-100)
- Platform-specific insights
- Personalized recommendations
- 30-day improvement action plan

**Analysis Criteria:**
- Profile completeness
- Activity level
- Community engagement
- Content quality
- Professional network

---

## 3. Architecture

### 3.1 Current Architecture

```
┌─────────────────────────────────────────┐
│         Streamlit Frontend              │
│  (Multi-page app with 4 main pages)    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Application Layer               │
│  - File Parser                          │
│  - Resume Analyzer                      │
│  - Resume Rewriter                      │
│  - Job Matcher                          │
│  - Footprint Scanner                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Utility Layer                   │
│  - Text Processing                      │
│  - Skill Extraction                     │
│  - ATS Scoring                          │
│  - Similarity Calculation               │
└─────────────────────────────────────────┘
```

### 3.2 Future API Architecture

```
┌─────────────────┐
│   Frontend      │ (React/Streamlit)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Gateway   │ (FastAPI/Django)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌─────────┐
│ Service │ │  Queue  │ (Celery)
│  Layer  │ │         │
└────┬────┘ └────┬────┘
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│Database │ │  Cache  │ (Redis)
│(Postgres│ │         │
└─────────┘ └─────────┘
```

---

## 4. Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/cv-ai-.git
cd cv-ai-

# Run setup script
chmod +x setup.sh
./setup.sh

# Run application
./run.sh
```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

---

## 5. Usage

### 5.1 Resume Review

1. Navigate to "Resume Reviewer" page
2. Upload your resume (PDF, DOCX, or TXT)
3. Click "Analyze Resume"
4. Review your scores and insights
5. Explore different tabs for detailed analysis

### 5.2 Resume Rewrite

1. Navigate to "Resume Rewriter" page
2. Upload your resume
3. Choose options (include analysis, show examples)
4. Click "Generate Rewriting Suggestions"
5. Review suggestions and apply improvements

### 5.3 Job Matching

1. Navigate to "Job Matcher" page
2. Choose input method:
   - Upload resume (automatic extraction)
   - Manual input (enter skills and experience)
3. Apply filters (region, industry, level)
4. Click "Find Matching Jobs"
5. Review matches and skill recommendations

### 5.4 Footprint Scanning

1. Navigate to "Footprint Scanner" page
2. Enter platform URLs/usernames:
   - LinkedIn profile URL
   - GitHub username
   - StackOverflow profile URL
3. Click "Scan Digital Footprint"
4. Review overall score and platform-specific insights
5. Follow recommendations for improvement

---

## 6. Project Structure

```
cv-ai-/
├── app.py                      # Main application
├── pages/                      # Streamlit pages
│   ├── 1_📄_Resume_Reviewer.py
│   ├── 2_✍️_Resume_Rewriter.py
│   ├── 3_🎯_Job_Matcher.py
│   └── 4_🌐_Footprint_Scanner.py
├── src/                        # Core logic
│   ├── config.py              # Configuration
│   ├── core/                  # Core modules
│   │   ├── resume_analyzer.py
│   │   ├── resume_rewriter.py
│   │   ├── job_matcher.py
│   │   └── footprint_scanner.py
│   └── utils/                 # Utilities
│       ├── file_parser.py
│       └── helpers.py
├── docs/                      # Documentation
│   └── API_STRUCTURE.md
├── data/                      # Data directory
├── temp/                      # Temporary files
├── models/                    # ML models (future)
├── requirements.txt           # Dependencies
├── setup.sh                   # Setup script
├── run.sh                     # Run script
├── .env.example              # Environment template
├── .gitignore                # Git ignore
└── README.md                 # Main README
```

---

## 7. Modules

### 7.1 Resume Analyzer (`src/core/resume_analyzer.py`)

**Class:** `ResumeAnalyzer`

**Methods:**
- `analyze(resume_text)`: Main analysis method
- `_extract_contact_info()`: Extract email, phone, URLs
- `_detect_sections()`: Identify resume sections
- `_estimate_experience()`: Calculate years of experience
- `_detect_education_level()`: Determine education level
- `_analyze_strengths_weaknesses()`: SWOT analysis
- `_calculate_overall_score()`: Calculate final score
- `_generate_suggestions()`: Create improvement tips

### 7.2 Resume Rewriter (`src/core/resume_rewriter.py`)

**Class:** `ResumeRewriter`

**Methods:**
- `rewrite(resume_text, analysis)`: Main rewriting method
- `_detect_weak_phrases()`: Find weak language
- `_suggest_action_verbs()`: Recommend strong verbs
- `_find_quantification_opportunities()`: Identify metrics gaps
- `_suggest_formatting_improvements()`: Format recommendations
- `_generate_optimized_sections()`: Create examples

### 7.3 Job Matcher (`src/core/job_matcher.py`)

**Class:** `JobMatcher`

**Methods:**
- `match_jobs(candidate_profile, region)`: Match algorithm
- `_calculate_match_score()`: Score calculation
- `get_regional_insights(region)`: Market insights
- `recommend_skill_development()`: Skill recommendations

### 7.4 Footprint Scanner (`src/core/footprint_scanner.py`)

**Class:** `FootprintScanner`

**Methods:**
- `analyze_footprint(linkedin, github, stackoverflow)`: Main scan
- `_analyze_linkedin()`: LinkedIn analysis
- `_analyze_github()`: GitHub analysis
- `_analyze_stackoverflow()`: StackOverflow analysis
- `_validate_*_url()`: URL validators

### 7.5 File Parser (`src/utils/file_parser.py`)

**Functions:**
- `parse_pdf(file_bytes)`: Extract text from PDF
- `parse_docx(file_bytes)`: Extract text from DOCX
- `parse_txt(file_bytes)`: Extract text from TXT
- `parse_file(filename, file_bytes)`: Main parser

### 7.6 Helpers (`src/utils/helpers.py`)

**Functions:**
- `clean_text()`: Text cleaning
- `extract_email()`: Email extraction
- `extract_phone()`: Phone extraction
- `calculate_similarity()`: Text similarity
- `calculate_ats_score()`: ATS scoring
- `extract_skills_from_text()`: Skill extraction

---

## 8. Future Enhancements

### 8.1 Immediate (Phase 2)

- [ ] Advanced NLP with spaCy/Transformers
- [ ] OpenAI API integration for better rewriting
- [ ] Real platform API integration (LinkedIn, GitHub, SO)
- [ ] User authentication and profiles
- [ ] Analysis history and tracking
- [ ] PDF report generation
- [ ] Email notifications

### 8.2 Medium-term

- [ ] FastAPI backend implementation
- [ ] PostgreSQL database
- [ ] Redis caching
- [ ] Celery background tasks
- [ ] Advanced job matching algorithm
- [ ] Resume templates
- [ ] Interview preparation module
- [ ] Salary insights

### 8.3 Long-term

- [ ] Mobile application
- [ ] AI-powered interview simulator
- [ ] Career path recommendations
- [ ] Skill gap analysis with learning resources
- [ ] Networking opportunities
- [ ] Employer dashboard
- [ ] Job application tracking
- [ ] Success metrics and analytics

---

## 9. Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/cv-ai-.git
cd cv-ai-

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run app.py --server.runOnSave true
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions/classes
- Keep functions focused and modular
- Write meaningful commit messages

### Testing

```bash
# Install testing dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=src
```

### Pull Request Process

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📊 Statistics

- **Lines of Code**: ~3,000+
- **Modules**: 8 core modules
- **Features**: 4 main features
- **Supported File Formats**: 4 (PDF, DOCX, DOC, TXT)
- **Technical Skills Tracked**: 50+
- **Soft Skills Tracked**: 15+
- **Sample Jobs**: 10+
- **Regions Covered**: 4

---

## 🏆 Achievements

- ✅ Modular, maintainable code structure
- ✅ API-ready architecture
- ✅ Professional UI/UX with Streamlit
- ✅ Comprehensive documentation
- ✅ Regional focus on MENA and Africa
- ✅ Multiple analysis algorithms
- ✅ Easy setup and deployment

---

## 📞 Support

For issues, questions, or contributions:
- GitHub Issues: [Report Bug](https://github.com/yourusername/cv-ai-/issues)
- Email: [Contact](mailto:support@example.com)
- Documentation: [Wiki](https://github.com/yourusername/cv-ai-/wiki)

---

**Built with ❤️ for IEEE TSYP13 Technical Challenge**

*Empowering careers across Africa and MENA regions*
