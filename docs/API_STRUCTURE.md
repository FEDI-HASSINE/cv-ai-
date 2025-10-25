# API Structure Documentation

## Overview

This document outlines the API structure for future backend integration. The current Streamlit application is designed with a modular architecture that can easily be converted to a REST API using Django, FastAPI, or Flask.

## Architecture

```
┌─────────────────┐
│   Frontend      │
│  (Streamlit/    │
│    React)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Gateway   │
│  (Django/       │
│   FastAPI)      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌─────────┐
│ Service │ │  Queue  │
│  Layer  │ │ (Celery)│
└────┬────┘ └────┬────┘
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│Database │ │  Cache  │
│(Postgres│ │ (Redis) │
└─────────┘ └─────────┘
```

## API Endpoints

### 1. Resume Analysis API

#### POST `/api/v1/resume/analyze`

Upload and analyze resume.

**Request:**
```json
{
  "file": "<base64_encoded_file>",
  "filename": "resume.pdf",
  "options": {
    "include_skills": true,
    "include_ats_score": true
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "overall_score": 85,
    "ats_score": 78,
    "technical_skills": ["Python", "JavaScript", "React"],
    "soft_skills": ["Leadership", "Communication"],
    "experience_years": 5.5,
    "education_level": "Bachelor's",
    "sections_found": ["Summary", "Experience", "Education"],
    "strengths": ["Well-structured resume", "Strong technical skills"],
    "weaknesses": ["Missing certifications section"],
    "suggestions": ["Add quantifiable metrics", "Include project section"]
  }
}
```

---

#### GET `/api/v1/resume/analysis/{analysis_id}`

Retrieve previous analysis.

**Response:**
```json
{
  "status": "success",
  "data": {
    "analysis_id": "uuid-here",
    "created_at": "2024-01-01T12:00:00Z",
    "resume_data": { /* analysis data */ }
  }
}
```

---

### 2. Resume Rewriter API

#### POST `/api/v1/resume/rewrite`

Get rewriting suggestions.

**Request:**
```json
{
  "file": "<base64_encoded_file>",
  "filename": "resume.pdf",
  "analysis_id": "uuid-here",  // optional
  "options": {
    "include_examples": true,
    "focus_areas": ["action_verbs", "quantification"]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "improvement_score": 75,
    "weak_phrases": [
      {
        "phrase": "responsible for",
        "alternative": "managed",
        "context": "...",
        "improved": "..."
      }
    ],
    "action_verbs": {
      "Leadership": ["Led", "Directed", "Managed"],
      "Achievement": ["Achieved", "Accomplished"]
    },
    "quantification_opportunities": [
      {
        "context": "...",
        "suggestion": "Add metrics: 'Improved X by Y%'"
      }
    ],
    "recommendations": [
      {
        "priority": "High",
        "category": "Language",
        "recommendation": "Replace weak phrases",
        "impact": "Significantly improves readability"
      }
    ]
  }
}
```

---

### 3. Job Matcher API

#### POST `/api/v1/jobs/match`

Match jobs based on candidate profile.

**Request:**
```json
{
  "candidate_profile": {
    "technical_skills": ["Python", "Django", "React"],
    "soft_skills": ["Leadership", "Communication"],
    "experience_years": 5,
    "education_level": "Bachelor's",
    "preferred_regions": ["MENA", "Global"],
    "preferred_industries": ["Technology", "Fintech"]
  },
  "filters": {
    "region": "MENA",
    "industry": ["Technology"],
    "level": ["Senior", "Mid-Level"],
    "remote_only": false
  },
  "limit": 10
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_matches": 15,
    "returned": 10,
    "jobs": [
      {
        "id": "JOB001",
        "title": "Senior Software Engineer",
        "company": "TechCorp MENA",
        "location": "Dubai, UAE",
        "region": "MENA",
        "industry": "Technology",
        "level": "Senior",
        "match_percentage": 92,
        "match_details": {
          "total_score": 0.92,
          "skill_score": 0.95,
          "experience_score": 1.0,
          "required_skills_matched": 5,
          "required_skills_total": 6,
          "missing_skills": ["Kubernetes"]
        },
        "required_skills": ["Python", "Django", "AWS"],
        "preferred_skills": ["Kubernetes", "Redis"],
        "salary_range": "$80,000 - $120,000",
        "remote": true,
        "description": "..."
      }
    ]
  }
}
```

---

#### GET `/api/v1/jobs/insights/{region}`

Get regional market insights.

**Response:**
```json
{
  "status": "success",
  "data": {
    "region": "MENA",
    "total_jobs": 150,
    "top_industries": {
      "Technology": 50,
      "Finance": 30
    },
    "top_skills": {
      "Python": 45,
      "JavaScript": 38
    },
    "avg_experience_required": 4.2,
    "regional_skills": ["Arabic", "English", "Technology"]
  }
}
```

---

#### POST `/api/v1/jobs/recommendations/skills`

Get skill development recommendations.

**Request:**
```json
{
  "current_skills": ["Python", "Django"],
  "target_region": "MENA"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "skill": "AWS",
        "demand_score": 15,
        "priority": "High",
        "reason": "Required/preferred in 15 job postings"
      }
    ]
  }
}
```

---

### 4. Footprint Scanner API

#### POST `/api/v1/footprint/scan`

Scan digital footprint.

**Request:**
```json
{
  "platforms": {
    "linkedin_url": "https://linkedin.com/in/user",
    "github_username": "username",
    "stackoverflow_url": "https://stackoverflow.com/users/123/name"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "overall_score": 75,
    "platforms_analyzed": ["LinkedIn", "GitHub", "StackOverflow"],
    "linkedin": {
      "score": 80,
      "profile_url": "...",
      "insights": [
        {
          "category": "Profile Completeness",
          "status": "Good",
          "description": "..."
        }
      ],
      "stats": {
        "connections": 500,
        "posts_last_month": 5,
        "engagement_rate": 0.12
      }
    },
    "github": {
      "score": 70,
      "username": "username",
      "stats": {
        "public_repos": 25,
        "followers": 100,
        "contributions_last_year": 450
      }
    },
    "stackoverflow": {
      "score": 65,
      "stats": {
        "reputation": 1500,
        "badges": {"gold": 1, "silver": 5, "bronze": 20},
        "answers": 45,
        "questions": 12
      }
    },
    "recommendations": [
      {
        "priority": "High",
        "recommendation": "Increase GitHub activity",
        "impact": "Demonstrates continuous learning"
      }
    ]
  }
}
```

---

### 5. User Management API

#### POST `/api/v1/auth/register`

Register new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "user_id": "uuid",
    "email": "user@example.com",
    "token": "jwt_token"
  }
}
```

---

#### POST `/api/v1/auth/login`

User login.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "user_id": "uuid",
    "token": "jwt_token",
    "refresh_token": "refresh_jwt_token"
  }
}
```

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Resume Analyses Table

```sql
CREATE TABLE resume_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255),
    file_hash VARCHAR(64),
    overall_score INTEGER,
    ats_score INTEGER,
    analysis_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Job Matches Table

```sql
CREATE TABLE job_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    job_id VARCHAR(50),
    match_score DECIMAL(3,2),
    match_details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Footprint Scans Table

```sql
CREATE TABLE footprint_scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    overall_score INTEGER,
    platforms JSONB,
    scan_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Error Handling

All API endpoints return errors in a consistent format:

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "Unsupported file format. Please upload PDF, DOCX, or TXT.",
    "details": {
      "allowed_formats": [".pdf", ".docx", ".txt"]
    }
  }
}
```

### Error Codes

- `INVALID_FILE_FORMAT`: Unsupported file type
- `FILE_TOO_LARGE`: File exceeds size limit
- `PARSING_ERROR`: Error parsing file content
- `INVALID_REQUEST`: Missing or invalid parameters
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

---

## Authentication

Use JWT (JSON Web Tokens) for authentication:

```
Authorization: Bearer <jwt_token>
```

---

## Rate Limiting

- **Free tier**: 10 requests/minute
- **Premium tier**: 100 requests/minute
- **Enterprise**: Custom limits

---

## Webhooks (Future)

Register webhooks for asynchronous processing:

```json
POST /api/v1/webhooks/register
{
  "url": "https://your-app.com/webhook",
  "events": ["analysis_complete", "jobs_matched"]
}
```

---

## Implementation Guide

### 1. Backend Framework Choice

**Recommended: FastAPI**

```python
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

app = FastAPI()

class ResumeAnalysisResponse(BaseModel):
    status: str
    data: dict

@app.post("/api/v1/resume/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(file: UploadFile = File(...)):
    # Import existing analyzer
    from src.core.resume_analyzer import ResumeAnalyzer
    from src.utils.file_parser import parse_file
    
    # Parse file
    content = await file.read()
    parsed = parse_file(file.filename, content)
    
    # Analyze
    analyzer = ResumeAnalyzer()
    analysis = analyzer.analyze(parsed["text"])
    
    return {"status": "success", "data": analysis}
```

### 2. Database Integration

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/utopiahire"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

### 3. Caching with Redis

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_analysis(file_hash):
    cached = redis_client.get(f"analysis:{file_hash}")
    if cached:
        return json.loads(cached)
    return None

def cache_analysis(file_hash, analysis, ttl=3600):
    redis_client.setex(
        f"analysis:{file_hash}",
        ttl,
        json.dumps(analysis)
    )
```

### 4. Background Tasks with Celery

```python
from celery import Celery

celery_app = Celery('utopiahire', broker='redis://localhost:6379/0')

@celery_app.task
def analyze_resume_async(file_content, filename):
    from src.core.resume_analyzer import ResumeAnalyzer
    from src.utils.file_parser import parse_file
    
    parsed = parse_file(filename, file_content)
    analyzer = ResumeAnalyzer()
    return analyzer.analyze(parsed["text"])
```

---

## Deployment

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/utopiahire
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=utopiahire
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
  
  celery:
    build: .
    command: celery -A tasks worker --loglevel=info
    depends_on:
      - redis
      - db

volumes:
  postgres_data:
```

---

## Testing

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_analyze_resume():
    with open("test_resume.pdf", "rb") as f:
        response = client.post(
            "/api/v1/resume/analyze",
            files={"file": ("resume.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "overall_score" in response.json()["data"]
```

---

## Next Steps

1. Choose backend framework (FastAPI recommended)
2. Set up database (PostgreSQL)
3. Implement authentication (JWT)
4. Add caching layer (Redis)
5. Set up background tasks (Celery)
6. Containerize with Docker
7. Deploy to cloud (AWS/GCP/Azure)
8. Add monitoring (Prometheus/Grafana)
9. Implement CI/CD pipeline
10. Add comprehensive testing

---

**This API structure is ready to be implemented and will seamlessly integrate with the existing codebase!**
