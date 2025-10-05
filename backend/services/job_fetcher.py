"""Job fetching service using JobSpy for real-time scraping."""
from typing import List, Dict, Any
from datetime import datetime
from jobspy import scrape_jobs
from config import get_settings
from utils import get_logger

logger = get_logger(__name__)
settings = get_settings()


class JobFetcher:
    """Fetch jobs from multiple sources using JobSpy."""
    
    def __init__(self):
        self.sources = settings.job_sources
        self.search_term = settings.job_search_term
        self.location = settings.job_location
        self.results_wanted = settings.job_results_wanted
        self.hours_old = settings.job_hours_old
        self.is_remote = settings.job_is_remote
        self.job_type = settings.job_type if settings.job_type else None
        self.country_indeed = settings.job_country_indeed
        self.proxy = settings.proxy_url if settings.proxy_url else None
    
    async def fetch_jobs(
        self, 
        search_term: str = None,
        location: str = None,
        sources: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch jobs from specified sources using JobSpy.
        
        Args:
            search_term: Job search keywords (overrides config)
            location: Job location (overrides config)
            sources: List of sources to scrape (overrides config)
        
        Returns:
            Raw JobSpy job dictionaries. Normalization happens in the LangGraph pipeline.
        """
        search_term = search_term or self.search_term
        location = location or self.location
        sources = sources or self.sources
        
        logger.info(f"Fetching jobs via JobSpy: '{search_term}' in '{location}'")
        logger.info(f"Sources: {sources}, Results wanted: {self.results_wanted}")
        
        try:
            jobs_df = scrape_jobs(
                site_name=sources,
                search_term=search_term,
                location=location,
                results_wanted=self.results_wanted,
                hours_old=self.hours_old,
                country_indeed=self.country_indeed,
                is_remote=self.is_remote,
                job_type=self.job_type,
                proxy=self.proxy
            )
            
            if jobs_df is None or jobs_df.empty:
                logger.warning("No jobs found")
                return []
            
            # Return raw records; normalization is handled in the LangGraph pipeline
            jobs_list = jobs_df.to_dict('records')
            logger.info(f"Fetched {len(jobs_list)} raw jobs from JobSpy")
            return jobs_list
            
        except Exception as e:
            logger.error(f"Error fetching jobs with JobSpy: {e}")
            return []
