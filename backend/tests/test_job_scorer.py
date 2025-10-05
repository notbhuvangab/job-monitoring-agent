"""Tests for job scorer service."""
import pytest
from services.job_scorer import JobScorer
from services.embeddings import generate_embedding


def test_score_job():
    """Test job scoring."""
    job_data = {
        "title": "Python Developer",
        "description": "Looking for a Python developer with React and PostgreSQL experience. Docker knowledge is a plus.",
        "company": "Tech Corp"
    }
    
    resume_data = {
        "skills": ["python", "react", "postgresql", "docker"],
        "embedding": generate_embedding("Python developer with React, PostgreSQL, and Docker experience")
    }
    
    score, details = JobScorer.score_job(job_data, resume_data)
    
    assert 0 <= score <= 100
    assert "embedding_score" in details
    assert "keyword_score" in details
    assert "matched_keywords" in details
    assert len(details["matched_keywords"]) > 0


def test_keyword_match():
    """Test keyword matching."""
    job_data = {
        "title": "Python Developer",
        "description": "We need Python, Django, and React skills"
    }
    
    resume_skills = ["python", "django", "react", "docker"]
    
    score, matched = JobScorer._calculate_keyword_match(job_data, resume_skills)
    
    assert score > 0
    assert "python" in matched
    assert "django" in matched
    assert "react" in matched


def test_batch_scoring():
    """Test batch job scoring."""
    jobs = [
        {"title": "Python Dev", "description": "Python and React"},
        {"title": "Java Dev", "description": "Java and Spring"},
    ]
    
    resume_data = {
        "skills": ["python", "react"],
        "embedding": generate_embedding("Python and React developer")
    }
    
    results = JobScorer.batch_score_jobs(jobs, resume_data)
    
    assert len(results) == 2
    assert all(0 <= result[1] <= 100 for result in results)
