"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator
import logging
from contextlib import contextmanager

from .models import Base
from ..security.secrets_manager import get_secrets_manager

logger = logging.getLogger(__name__)

# Database engine (will be initialized)
engine = None
SessionLocal = None


def get_database_url() -> str:
    """
    Get database URL from secrets manager
    Falls back to SQLite for development if not configured
    """
    secrets = get_secrets_manager()
    db_url = secrets.get_database_url()
    
    if db_url:
        return db_url
    
    # Fallback to SQLite for development
    logger.warning("DATABASE_URL not configured, using SQLite fallback")
    import os
    from pathlib import Path
    
    db_dir = Path(__file__).parent.parent.parent / "data"
    db_dir.mkdir(exist_ok=True)
    db_path = db_dir / "utopiahire.db"
    
    return f"sqlite:///{db_path}"


def init_db(database_url: str = None):
    """
    Initialize database connection
    
    Args:
        database_url: Optional database URL override
    """
    global engine, SessionLocal
    
    if database_url is None:
        database_url = get_database_url()
    
    logger.info(f"Initializing database connection...")
    
    # Create engine
    if database_url.startswith("sqlite"):
        # SQLite specific settings
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=False
        )
    else:
        # PostgreSQL settings
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=10,
            max_overflow=20,
            echo=False
        )
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    logger.info("Database connection initialized")


def create_tables():
    """Create all database tables"""
    if engine is None:
        init_db()
    
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


def drop_tables():
    """Drop all database tables (use with caution!)"""
    if engine is None:
        init_db()
    
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Database tables dropped")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session
    
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    if SessionLocal is None:
        init_db()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session
    
    Usage:
        with get_db_context() as db:
            users = db.query(User).all()
    """
    if SessionLocal is None:
        init_db()
    
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


# Initialize on import if DATABASE_URL is set
try:
    secrets = get_secrets_manager()
    if secrets.get_database_url():
        init_db()
        logger.info("Database initialized from environment")
except Exception as e:
    logger.warning(f"Database not initialized: {e}")
