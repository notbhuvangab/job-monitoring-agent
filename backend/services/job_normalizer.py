"""Job normalization service."""
from typing import Dict, Any
from datetime import datetime
from utils import get_logger

logger = get_logger(__name__)


class JobNormalizer:
    """Normalize job data from various sources into consistent schema."""
    
    @staticmethod
    def normalize(raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw job data into consistent schema.
        
        Args:
            raw_job: Raw job data from fetcher
        
        Returns:
            Normalized job data matching our schema
        """
        try:
            # Handle different field names from different sources
            normalized = {
                "job_id": raw_job.get("external_id") or raw_job.get("id") or raw_job.get("job_id"),
                "title": raw_job.get("title") or raw_job.get("job_title", "Unknown Title"),
                "company": raw_job.get("company") or raw_job.get("company_name", "Unknown Company"),
                "description": raw_job.get("description") or raw_job.get("job_description", ""),
                "location": raw_job.get("location") or raw_job.get("job_location", ""),
                "type": JobNormalizer._normalize_job_type(raw_job.get("type") or raw_job.get("work_type", "")),
                "apply_url": raw_job.get("apply_url") or raw_job.get("url") or raw_job.get("link", ""),
                "timestamp_fetched": JobNormalizer._parse_timestamp(raw_job.get("timestamp")),
            }
            
            # Validate required fields
            if not normalized["job_id"]:
                logger.error("Missing job_id in raw job data")
                return None
            
            if not normalized["description"]:
                logger.warning(f"Job {normalized['job_id']} has no description")
            
            logger.debug(f"Normalized job: {normalized['job_id']} - {normalized['title']}")
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing job: {e}")
            return None
    
    @staticmethod
    def _normalize_job_type(job_type: str) -> str:
        """Normalize job type to one of: remote, hybrid, onsite."""
        if not job_type:
            return "onsite"  # Default
        
        job_type_lower = job_type.lower()
        
        if "remote" in job_type_lower:
            return "remote"
        elif "hybrid" in job_type_lower:
            return "hybrid"
        else:
            return "onsite"
    
    @staticmethod
    def _parse_timestamp(timestamp: Any) -> datetime:
        """Parse timestamp from various formats."""
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                pass
        
        # Default to now
        return datetime.now()
    
    @staticmethod
    def batch_normalize(raw_jobs: list[Dict[str, Any]]):
        """Deprecated: batch normalization is unused; use pipeline per job."""
        raise NotImplementedError("batch_normalize is removed; process per-job via pipeline")

