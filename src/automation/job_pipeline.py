"""
Job Scraping Pipeline
Orchestrates job scraping, parsing, and storage
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class JobScrapingPipeline:
    """
    Complete pipeline for job scraping, parsing, and storage
    """
    
    def __init__(self, use_database: bool = True):
        """
        Initialize scraping pipeline
        
        Args:
            use_database: Whether to store results in database
        """
        self.use_database = use_database
        self.scraper = None
        self.parser = None
        
        # Initialize components
        self._init_scraper()
        self._init_parser()
    
    def _init_scraper(self):
        """Initialize job scraper"""
        try:
            from ..core.job_scraper import JobScraper
            self.scraper = JobScraper()
            logger.info("Job scraper initialized")
        except Exception as e:
            logger.error(f"Failed to initialize scraper: {e}")
    
    def _init_parser(self):
        """Initialize job parser for skill extraction"""
        try:
            from .job_parser import JobParser
            self.parser = JobParser()
            logger.info("Job parser initialized")
        except Exception as e:
            logger.warning(f"Job parser not available: {e}")
    
    def run(
        self,
        keywords: List[str],
        regions: List[str],
        max_results_per_region: int = 20
    ) -> Dict[str, Any]:
        """
        Run complete scraping pipeline
        
        Args:
            keywords: Search keywords
            regions: Target regions
            max_results_per_region: Max results per region
            
        Returns:
            Dict with run statistics
        """
        start_time = datetime.now()
        
        stats = {
            'started_at': start_time.isoformat(),
            'keywords': keywords,
            'regions': regions,
            'jobs_found': 0,
            'jobs_new': 0,
            'jobs_updated': 0,
            'jobs_failed': 0,
            'errors': []
        }
        
        # Create scraping run record if using database
        run_id = None
        if self.use_database:
            run_id = self._create_scraping_run(keywords, regions[0] if regions else "Global")
        
        try:
            # Scrape jobs from all regions
            all_jobs = []
            for region in regions:
                logger.info(f"Scraping jobs for region: {region}")
                
                try:
                    jobs = self.scraper.search_regional_jobs(
                        keywords=keywords,
                        region=region,
                        max_results=max_results_per_region
                    )
                    
                    logger.info(f"Found {len(jobs)} jobs in {region}")
                    all_jobs.extend(jobs)
                    stats['jobs_found'] += len(jobs)
                    
                except Exception as e:
                    logger.error(f"Error scraping {region}: {e}")
                    stats['errors'].append(f"{region}: {str(e)}")
            
            # Parse and enhance jobs
            if self.parser:
                logger.info("Parsing and enhancing job descriptions...")
                all_jobs = self._parse_jobs(all_jobs)
            
            # Store in database
            if self.use_database and all_jobs:
                logger.info("Storing jobs in database...")
                new_count, updated_count = self._store_jobs(all_jobs)
                stats['jobs_new'] = new_count
                stats['jobs_updated'] = updated_count
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            stats['duration_seconds'] = duration
            stats['completed_at'] = datetime.now().isoformat()
            stats['status'] = 'completed'
            
            # Update scraping run
            if run_id:
                self._update_scraping_run(run_id, stats)
            
            logger.info(f"Scraping completed: {stats['jobs_found']} found, "
                       f"{stats['jobs_new']} new, {stats['jobs_updated']} updated")
            
            return stats
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            stats['status'] = 'failed'
            stats['error_message'] = str(e)
            
            if run_id:
                self._update_scraping_run(run_id, stats)
            
            raise
    
    def _parse_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse and enhance job descriptions
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Enhanced jobs with extracted skills, requirements, etc.
        """
        enhanced_jobs = []
        
        for job in jobs:
            try:
                # Parse job description
                if job.get('description'):
                    parsed = self.parser.parse(job['description'])
                    
                    # Add parsed fields
                    if parsed.get('required_skills'):
                        job['required_skills'] = parsed['required_skills']
                    if parsed.get('preferred_skills'):
                        job['preferred_skills'] = parsed['preferred_skills']
                    if parsed.get('experience_level'):
                        job['experience_level'] = parsed['experience_level']
                    if parsed.get('job_type'):
                        job['job_type'] = parsed['job_type']
                
                enhanced_jobs.append(job)
                
            except Exception as e:
                logger.warning(f"Failed to parse job {job.get('title', 'Unknown')}: {e}")
                enhanced_jobs.append(job)  # Keep original
        
        return enhanced_jobs
    
    def _create_scraping_run(self, keywords: List[str], region: str) -> int:
        """Create scraping run record in database"""
        try:
            from ..database import get_db_context
            from ..database.models import JobScrapingRun
            
            with get_db_context() as db:
                run = JobScrapingRun(
                    source="multi_source",
                    keywords=keywords,
                    region=region,
                    status="running"
                )
                db.add(run)
                db.flush()
                return run.id
                
        except Exception as e:
            logger.error(f"Failed to create scraping run: {e}")
            return None
    
    def _update_scraping_run(self, run_id: int, stats: Dict[str, Any]):
        """Update scraping run with results"""
        try:
            from ..database import get_db_context
            from ..database.models import JobScrapingRun
            
            with get_db_context() as db:
                run = db.query(JobScrapingRun).filter(JobScrapingRun.id == run_id).first()
                if run:
                    run.jobs_found = stats.get('jobs_found', 0)
                    run.jobs_new = stats.get('jobs_new', 0)
                    run.jobs_updated = stats.get('jobs_updated', 0)
                    run.jobs_failed = stats.get('jobs_failed', 0)
                    run.status = stats.get('status', 'completed')
                    run.error_message = stats.get('error_message')
                    run.duration_seconds = stats.get('duration_seconds')
                    run.completed_at = datetime.now()
                
        except Exception as e:
            logger.error(f"Failed to update scraping run: {e}")
    
    def _store_jobs(self, jobs: List[Dict[str, Any]]) -> tuple:
        """
        Store or update jobs in database
        
        Returns:
            Tuple of (new_count, updated_count)
        """
        try:
            from ..database import get_db_context
            from ..database.models import Job, JobStatus
            
            new_count = 0
            updated_count = 0
            
            with get_db_context() as db:
                for job_data in jobs:
                    try:
                        # Check if job exists by URL or title+company
                        existing_job = None
                        
                        if job_data.get('url'):
                            existing_job = db.query(Job).filter(
                                Job.url == job_data['url']
                            ).first()
                        
                        if not existing_job and job_data.get('title') and job_data.get('company'):
                            existing_job = db.query(Job).filter(
                                Job.title == job_data['title'],
                                Job.company == job_data['company']
                            ).first()
                        
                        if existing_job:
                            # Update existing job
                            existing_job.description = job_data.get('description', existing_job.description)
                            existing_job.location = job_data.get('location', existing_job.location)
                            existing_job.last_seen = datetime.now()
                            existing_job.status = JobStatus.ACTIVE
                            
                            # Update skills if available
                            if job_data.get('required_skills'):
                                existing_job.required_skills = job_data['required_skills']
                            if job_data.get('preferred_skills'):
                                existing_job.preferred_skills = job_data['preferred_skills']
                            
                            updated_count += 1
                        else:
                            # Create new job
                            new_job = Job(
                                title=job_data['title'],
                                company=job_data['company'],
                                location=job_data.get('location', ''),
                                description=job_data.get('description', ''),
                                source=job_data.get('source', 'scraper'),
                                url=job_data.get('url', ''),
                                required_skills=job_data.get('required_skills', []),
                                preferred_skills=job_data.get('preferred_skills', []),
                                experience_level=job_data.get('experience_level'),
                                job_type=job_data.get('job_type'),
                                is_remote=job_data.get('is_remote', False),
                                status=JobStatus.ACTIVE,
                                posted_date=datetime.now()
                            )
                            db.add(new_job)
                            new_count += 1
                    
                    except Exception as e:
                        logger.error(f"Failed to store job: {e}")
                        continue
            
            logger.info(f"Stored {new_count} new jobs, updated {updated_count} jobs")
            return new_count, updated_count
            
        except Exception as e:
            logger.error(f"Database storage error: {e}")
            return 0, 0


def run_scraping_pipeline(
    keywords: List[str] = None,
    regions: List[str] = None,
    max_results: int = 20
) -> Dict[str, Any]:
    """
    Convenience function to run scraping pipeline
    
    Args:
        keywords: Search keywords (default: common tech keywords)
        regions: Target regions (default: all)
        max_results: Max results per region
        
    Returns:
        Statistics dictionary
    """
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
