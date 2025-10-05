"""Job fetching scheduler."""
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from config import get_settings
from database import SessionLocal
from models import Job, Resume, JobStatus, JobLabel
from services import JobFetcher
from pipeline import JobProcessingPipeline
from api.websocket_manager import manager
from utils import get_logger

logger = get_logger(__name__)
settings = get_settings()


class JobScheduler:
    """Scheduler for periodic job fetching and processing."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.fetcher = JobFetcher()
        self.pipeline = JobProcessingPipeline()
        self.is_running = False
        self.last_fetch_time = None
        self.next_fetch_time = None
        self.fetch_interval_minutes = settings.job_fetch_interval_minutes
    
    async def fetch_and_process_jobs(self):
        """Fetch new jobs and process them through the pipeline."""
        if self.is_running:
            logger.warning("Previous job fetch is still running, skipping this cycle")
            return
        
        self.is_running = True
        self.last_fetch_time = datetime.now()
        logger.info("Starting scheduled job fetch and processing")
        
        db: Session = SessionLocal()
        
        try:
            # Get current resume (only one allowed)
            resume = db.query(Resume).first()
            
            if not resume:
                logger.warning("No resume found. Please upload a resume to start job processing.")
                return
            
            # Build resume data - LLM only needs the content!
            resume_data = {
                "content": resume.content if resume.content else ""
            }
            
            logger.info(f"Using resume: {len(resume_data['content'])} characters")
            
            # Fetch jobs
            logger.info("Fetching jobs from sources")
            raw_jobs = await self.fetcher.fetch_jobs()
            
            if not raw_jobs:
                logger.info("No new jobs fetched")
                return
            
            logger.info(f"Fetched {len(raw_jobs)} jobs")
            
            # Process each job through pipeline
            new_jobs_count = 0
            
            for raw_job in raw_jobs:
                try:
                    logger.info(f"Raw job: {raw_job}, Resume data : {resume_data}")
                    # Process through pipeline first to get normalized data
                    result = self.pipeline.process_job(raw_job, resume_data)
                    
                    if result.get("error"):
                        logger.error(f"Error processing job: {result['error']}")
                        continue
                    
                    apply_url = result["normalized_job"].get("apply_url")
                    if apply_url:
                        existing = db.query(Job).filter(Job.apply_url == apply_url).first()
                        if existing:
                            logger.debug(f"Job already exists (same URL): {result['normalized_job']['title']}")
                            continue
                    
                    # Store in database (already processed above)
                    job = Job(
                        job_id=result["job_id"],
                        title=result["normalized_job"]["title"],
                        company=result["normalized_job"]["company"],
                        description=result["normalized_job"]["description"],
                        location=result["normalized_job"].get("location"),
                        type=result["normalized_job"].get("type"),
                        apply_url=result["normalized_job"].get("apply_url"),
                        timestamp_fetched=result["normalized_job"].get("timestamp_fetched"),
                        status=JobStatus.CLASSIFIED,
                        score=result["score"],
                        label=JobLabel(result["label"]),
                        keywords_matched=result["score_details"].get("matched_keywords", []),
                        llm_reasoning=result["score_details"].get("llm_reasoning", "")
                    )
                    
                    db.add(job)
                    db.commit()
                    db.refresh(job)
                    
                    # Broadcast to WebSocket clients
                    await manager.broadcast_new_job(job.to_dict())
                    
                    new_jobs_count += 1
                    logger.info(f"Processed and stored job: {job.job_id} (score: {job.score})")
                    
                except Exception as e:
                    logger.error(f"Error processing individual job: {e}")
                    continue
            
            logger.info(f"Successfully processed {new_jobs_count} new jobs")
            
        except Exception as e:
            logger.error(f"Error in scheduled job fetch: {e}")
        finally:
            db.close()
            self.is_running = False
            self.last_fetch_time = datetime.now()
            self.next_fetch_time = datetime.now() + timedelta(minutes=self.fetch_interval_minutes)
    
    def start(self):
        """Start the scheduler."""
        # Schedule job fetching
        self.scheduler.add_job(
            self.fetch_and_process_jobs,
            trigger=IntervalTrigger(minutes=settings.job_fetch_interval_minutes),
            id="fetch_jobs",
            name="Fetch and process jobs",
            replace_existing=True
        )
        
        self.scheduler.start()
        self.next_fetch_time = datetime.now() + timedelta(minutes=self.fetch_interval_minutes)
        logger.info(f"Scheduler started. Will fetch jobs every {self.fetch_interval_minutes} minutes")
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    async def run_now(self):
        """Manually trigger job fetch and processing."""
        logger.info("Manually triggering job fetch")
        await self.fetch_and_process_jobs()

