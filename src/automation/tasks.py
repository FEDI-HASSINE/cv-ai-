"""
Celery tasks for automated job scraping
"""

from celery import Celery
from datetime import datetime, timedelta
import logging
from typing import List

logger = logging.getLogger(__name__)

# Initialize Celery
# In production, use Redis or RabbitMQ as broker
celery_app = Celery(
    'utopiahire',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50
)


@celery_app.task(name='scrape_jobs', bind=True, max_retries=3)
def scrape_jobs_task(self, keywords: List[str] = None, regions: List[str] = None):
    """
    Celery task for job scraping
    
    Args:
        keywords: Search keywords
        regions: Target regions
        
    Returns:
        Statistics dictionary
    """
    try:
        logger.info(f"Starting job scraping task: keywords={keywords}, regions={regions}")
        
        from .job_pipeline import run_scraping_pipeline
        
        stats = run_scraping_pipeline(keywords=keywords, regions=regions)
        
        logger.info(f"Job scraping completed: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Job scraping task failed: {e}")
        
        # Retry with exponential backoff
        try:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for job scraping task")
            raise


@celery_app.task(name='update_job_status')
def update_job_status_task():
    """
    Update job statuses (mark expired, inactive, etc.)
    """
    try:
        logger.info("Starting job status update task")
        
        from ..database import get_db_context
        from ..database.models import Job, JobStatus
        
        updated_count = 0
        
        with get_db_context() as db:
            # Mark jobs as expired if not seen in 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            
            expired_jobs = db.query(Job).filter(
                Job.status == JobStatus.ACTIVE,
                Job.last_seen < cutoff_date
            ).all()
            
            for job in expired_jobs:
                job.status = JobStatus.EXPIRED
                updated_count += 1
        
        logger.info(f"Updated {updated_count} jobs to expired status")
        return {'updated': updated_count}
        
    except Exception as e:
        logger.error(f"Job status update task failed: {e}")
        raise


@celery_app.task(name='cleanup_old_jobs')
def cleanup_old_jobs_task(days: int = 90):
    """
    Clean up old expired jobs
    
    Args:
        days: Delete jobs older than this many days
    """
    try:
        logger.info(f"Starting cleanup of jobs older than {days} days")
        
        from ..database import get_db_context
        from ..database.models import Job, JobStatus
        
        deleted_count = 0
        
        with get_db_context() as db:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            old_jobs = db.query(Job).filter(
                Job.status.in_([JobStatus.EXPIRED, JobStatus.FILLED]),
                Job.updated_at < cutoff_date
            ).all()
            
            for job in old_jobs:
                db.delete(job)
                deleted_count += 1
        
        logger.info(f"Deleted {deleted_count} old jobs")
        return {'deleted': deleted_count}
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        raise


@celery_app.task(name='build_job_index')
def build_job_index_task():
    """
    Rebuild vector search index for jobs
    """
    try:
        logger.info("Starting job index rebuild")
        
        from ..database import get_db_context
        from ..database.models import Job
        from ..nlp.vector_matcher import build_job_index
        from pathlib import Path
        
        # Get all active jobs from database
        with get_db_context() as db:
            jobs = db.query(Job).filter(Job.status == JobStatus.ACTIVE).all()
            
            job_dicts = [
                {
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'description': job.description or '',
                    'required_skills': job.required_skills or [],
                    'preferred_skills': job.preferred_skills or [],
                    'location': job.location,
                    'region': job.region,
                    'industry': job.industry
                }
                for job in jobs
            ]
        
        # Build index
        index_path = Path(__file__).parent.parent.parent / "data" / "job_index.faiss"
        matcher = build_job_index(job_dicts, index_path=index_path)
        
        logger.info(f"Built index with {len(job_dicts)} jobs")
        return {'jobs_indexed': len(job_dicts)}
        
    except Exception as e:
        logger.error(f"Index build task failed: {e}")
        raise


# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    'scrape-jobs-daily': {
        'task': 'scrape_jobs',
        'schedule': timedelta(hours=24),  # Run daily
        'args': (
            ['software engineer', 'data scientist', 'product manager'],
            ['MENA', 'Sub-Saharan Africa', 'North Africa']
        )
    },
    'update-job-status-hourly': {
        'task': 'update_job_status',
        'schedule': timedelta(hours=1),  # Run hourly
    },
    'cleanup-old-jobs-weekly': {
        'task': 'cleanup_old_jobs',
        'schedule': timedelta(days=7),  # Run weekly
        'args': (90,)  # Delete jobs older than 90 days
    },
    'rebuild-index-daily': {
        'task': 'build_job_index',
        'schedule': timedelta(hours=24),  # Run daily
    }
}
