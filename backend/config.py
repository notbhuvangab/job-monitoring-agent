"""Configuration management for the application."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    openai_api_key: str = ""
    
    # Database
    database_url: str = "sqlite:///./jobs.db"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Scheduler (Real scraping needs longer intervals to avoid rate limits)
    job_fetch_interval_minutes: int = 15
    
    # ===== JobSpy Configuration =====
    
    # Job Search Parameters
    job_search_term: str = "software engineer"  # Keywords to search
    job_location: str = "United States"  # Job location
    job_results_wanted: int = 20  # Results per source per fetch
    job_hours_old: int = 72  # Only jobs from last X hours
    
    # Job Sources (Supported: indeed, linkedin, zip_recruiter, glassdoor, google)
    job_sources: List[str] = ["indeed", "linkedin", "zip_recruiter"]
    
    job_is_remote: bool = False  # Set True to only fetch remote jobs
    job_type: str = ""  # Options: fulltime, parttime, internship, contract (empty = all)
    
    job_country_indeed: str = "USA"  # For Indeed: USA, UK, CA, etc.
    
    # Proxy Configuration (Optional - helps avoid rate limits)
    proxy_url: str = ""  # Format: http://username:password@proxy:port

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
