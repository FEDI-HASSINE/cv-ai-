"""
SQLAlchemy database models
Defines schema for PostgreSQL database
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, JSON, Text,
    ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    """User roles"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class JobStatus(enum.Enum):
    """Job posting status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    FILLED = "filled"
    ARCHIVED = "archived"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_matches = relationship("JobMatch", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_created', 'created_at'),
    )


class Resume(Base):
    """Resume/CV model"""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # File information
    filename = Column(String(255))
    file_path = Column(String(500))  # Encrypted file path
    file_size = Column(Integer)  # in bytes
    file_type = Column(String(50))  # pdf, docx, etc.
    
    # Extracted content
    raw_text = Column(Text)  # Extracted text
    
    # Analysis results (stored as JSON)
    analysis_results = Column(JSON)
    
    # Extracted fields
    candidate_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    
    # Skills (stored as JSON array)
    technical_skills = Column(JSON)
    soft_skills = Column(JSON)
    
    # Experience
    experience_years = Column(Float)
    job_title = Column(String(255))
    
    # Scores
    overall_score = Column(Integer)
    ats_score = Column(Integer)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    job_matches = relationship("JobMatch", back_populates="resume", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_resume_user', 'user_id'),
        Index('idx_resume_created', 'created_at'),
        Index('idx_resume_active', 'is_active'),
    )


class Job(Base):
    """Job posting model"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Job details
    external_id = Column(String(255), unique=True, index=True)  # ID from source
    title = Column(String(500), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    region = Column(String(100))  # MENA, Sub-Saharan Africa, etc.
    country = Column(String(100))
    city = Column(String(100))
    
    # Job content
    description = Column(Text)
    requirements = Column(Text)
    
    # Job metadata
    source = Column(String(100))  # LinkedIn, Indeed, etc.
    url = Column(String(1000))
    apply_url = Column(String(1000))
    
    # Job attributes
    industry = Column(String(100))
    job_type = Column(String(50))  # Full-time, Part-time, Contract
    experience_level = Column(String(50))  # Entry, Mid, Senior
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(10))
    is_remote = Column(Boolean, default=False)
    
    # Skills (JSON array)
    required_skills = Column(JSON)
    preferred_skills = Column(JSON)
    
    # Status
    status = Column(SQLEnum(JobStatus), default=JobStatus.ACTIVE)
    
    # Posting information
    posted_date = Column(DateTime(timezone=True))
    expires_date = Column(DateTime(timezone=True))
    
    # Internal tracking
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), onupdate=func.now())
    view_count = Column(Integer, default=0)
    apply_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job_matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    scraping_runs = relationship("JobScrapingRun", back_populates="jobs", 
                                secondary="job_scraping_association")
    
    # Indexes
    __table_args__ = (
        Index('idx_job_title', 'title'),
        Index('idx_job_company', 'company'),
        Index('idx_job_location', 'location'),
        Index('idx_job_region', 'region'),
        Index('idx_job_status', 'status'),
        Index('idx_job_posted', 'posted_date'),
        Index('idx_job_source', 'source'),
    )


class JobMatch(Base):
    """Job matching results"""
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    
    # Match scores
    match_percentage = Column(Integer)
    skill_score = Column(Float)
    experience_score = Column(Float)
    location_score = Column(Float)
    semantic_score = Column(Float)  # From vector matching
    
    # Match details (JSON)
    match_details = Column(JSON)  # Matched skills, missing skills, etc.
    
    # Match method
    match_method = Column(String(50))  # keyword, vector, hybrid
    
    # User interaction
    viewed = Column(Boolean, default=False)
    applied = Column(Boolean, default=False)
    saved = Column(Boolean, default=False)
    hidden = Column(Boolean, default=False)
    
    # Application tracking
    application_status = Column(String(50))  # Applied, Interview, Rejected, Offer
    application_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="job_matches")
    resume = relationship("Resume", back_populates="job_matches")
    job = relationship("Job", back_populates="job_matches")
    
    # Indexes
    __table_args__ = (
        Index('idx_match_user', 'user_id'),
        Index('idx_match_resume', 'resume_id'),
        Index('idx_match_job', 'job_id'),
        Index('idx_match_score', 'match_percentage'),
        Index('idx_match_created', 'created_at'),
    )


class JobScrapingRun(Base):
    """Track job scraping runs"""
    __tablename__ = "job_scraping_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Run details
    source = Column(String(100))  # LinkedIn, Indeed, etc.
    keywords = Column(JSON)  # Search keywords used
    region = Column(String(100))
    
    # Results
    jobs_found = Column(Integer, default=0)
    jobs_new = Column(Integer, default=0)
    jobs_updated = Column(Integer, default=0)
    jobs_failed = Column(Integer, default=0)
    
    # Status
    status = Column(String(50))  # Running, Completed, Failed
    error_message = Column(Text)
    
    # Performance
    duration_seconds = Column(Float)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    jobs = relationship("Job", back_populates="scraping_runs",
                       secondary="job_scraping_association")
    
    # Indexes
    __table_args__ = (
        Index('idx_scraping_source', 'source'),
        Index('idx_scraping_started', 'started_at'),
        Index('idx_scraping_status', 'status'),
    )


# Association table for many-to-many relationship
from sqlalchemy import Table

job_scraping_association = Table(
    'job_scraping_association',
    Base.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id', ondelete='CASCADE')),
    Column('scraping_run_id', Integer, ForeignKey('job_scraping_runs.id', ondelete='CASCADE')),
    Index('idx_assoc_job', 'job_id'),
    Index('idx_assoc_run', 'scraping_run_id'),
)
