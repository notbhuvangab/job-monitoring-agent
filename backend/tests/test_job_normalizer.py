"""Tests for job normalizer service."""
import pytest
from services.job_normalizer import JobNormalizer
from datetime import datetime


def test_normalize_valid_job():
    """Test normalizing a valid job."""
    raw_job = {
        "external_id": "test123",
        "title": "Software Engineer",
        "company": "Tech Corp",
        "description": "Great opportunity",
        "location": "Remote",
        "type": "remote",
        "apply_url": "https://example.com/apply",
        "timestamp": datetime.now().isoformat()
    }
    
    normalized = JobNormalizer.normalize(raw_job)
    
    assert normalized is not None
    assert normalized["job_id"] == "test123"
    assert normalized["title"] == "Software Engineer"
    assert normalized["company"] == "Tech Corp"
    assert normalized["type"] == "remote"


def test_normalize_missing_job_id():
    """Test normalizing job without ID."""
    raw_job = {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "description": "Great opportunity"
    }
    
    normalized = JobNormalizer.normalize(raw_job)
    assert normalized is None


def test_normalize_job_type():
    """Test job type normalization."""
    assert JobNormalizer._normalize_job_type("Remote Work") == "remote"
    assert JobNormalizer._normalize_job_type("Hybrid") == "hybrid"
    assert JobNormalizer._normalize_job_type("On-site") == "onsite"
    assert JobNormalizer._normalize_job_type("") == "onsite"


def test_batch_normalize():
    """Test batch normalization."""
    raw_jobs = [
        {
            "external_id": f"job{i}",
            "title": f"Role {i}",
            "company": f"Company {i}",
            "description": "Description",
            "timestamp": datetime.now().isoformat()
        }
        for i in range(3)
    ]
    
    normalized_jobs = JobNormalizer.batch_normalize(raw_jobs)
    
    assert len(normalized_jobs) == 3
    assert all(job["job_id"] for job in normalized_jobs)
