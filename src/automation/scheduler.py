"""
Scheduler for job scraping pipeline
Simple scheduler without Celery (for development/testing)
"""

import schedule
import time
from datetime import datetime
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def schedule_scraping(
    keywords: List[str] = None,
    regions: List[str] = None,
    interval_hours: int = 24
):
    """
    Schedule periodic job scraping (simple scheduler without Celery)
    
    Args:
        keywords: Search keywords
        regions: Target regions
        interval_hours: Scraping interval in hours
    """
    from .job_pipeline import run_scraping_pipeline
    
    def job():
        logger.info(f"Starting scheduled job scraping at {datetime.now()}")
        try:
            stats = run_scraping_pipeline(keywords=keywords, regions=regions)
            logger.info(f"Scheduled scraping completed: {stats}")
        except Exception as e:
            logger.error(f"Scheduled scraping failed: {e}")
    
    # Schedule the job
    schedule.every(interval_hours).hours.do(job)
    
    logger.info(f"Scheduled job scraping every {interval_hours} hours")
    
    # Run immediately once
    job()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


def run_scraping_pipeline(
    keywords: List[str] = None,
    regions: List[str] = None,
    max_results: int = 20
) -> dict:
    """
    Run scraping pipeline once
    
    Args:
        keywords: Search keywords
        regions: Target regions  
        max_results: Max results per region
        
    Returns:
        Statistics dictionary
    """
    from .job_pipeline import JobScrapingPipeline
    
    if keywords is None:
        keywords = [
            "software engineer", "data scientist", "product manager",
            "devops engineer", "full stack developer"
        ]
    
    if regions is None:
        from ..config import Config
        regions = Config.REGIONS
    
    pipeline = JobScrapingPipeline()
    return pipeline.run(keywords, regions, max_results)


if __name__ == "__main__":
    # Run scheduler
    logging.basicConfig(level=logging.INFO)
    schedule_scraping(interval_hours=24)
