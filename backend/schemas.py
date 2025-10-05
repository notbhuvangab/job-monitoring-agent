"""Pydantic schemas for API request/response - cleaned up."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from models import JobStatus, JobLabel


class JobResponse(BaseModel):
    """Schema for job API response."""
    id: int
    job_id: str
    title: str
    company: str
    description: str
    location: Optional[str] = None
    type: Optional[str] = None
    apply_url: Optional[str] = None
    status: JobStatus
    score: float = 0.0
    label: Optional[JobLabel] = None
    keywords_matched: Optional[List[str]] = None
    llm_reasoning: Optional[str] = None
    timestamp_fetched: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResumeResponse(BaseModel):
    """Schema for resume API response."""
    id: int
    filename: Optional[str] = None
    skills: Optional[List[str]] = None
    experiences: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
