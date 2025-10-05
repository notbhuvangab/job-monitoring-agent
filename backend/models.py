"""Database models."""
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from database import Base
import enum


class JobStatus(str, enum.Enum):
    """Job processing status."""
    PENDING = "pending"
    NORMALIZED = "normalized"
    SCORED = "scored"
    CLASSIFIED = "classified"
    FAILED = "failed"


class JobLabel(str, enum.Enum):
    """Job fit classification."""
    BEST_FIT = "best"
    MID_FIT = "mid"
    LEAST_FIT = "least"


class Job(Base):
    """Job posting model."""
    
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True, nullable=False)  # External job ID
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String)
    type = Column(String)  # remote / hybrid / onsite
    apply_url = Column(String, unique=True, index=True)  # UNIQUE - prevents duplicates
    timestamp_fetched = Column(DateTime, default=func.now())
    
    # Processing fields
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, index=True)
    score = Column(Float, default=0.0)
    label = Column(SQLEnum(JobLabel), nullable=True, index=True)
    
    # Scoring metadata
    keywords_matched = Column(JSON)  # Matched keywords
    llm_reasoning = Column(Text)  # LLM explanation of the score
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "description": self.description,
            "location": self.location,
            "type": self.type,
            "apply_url": self.apply_url,
            "timestamp_fetched": self.timestamp_fetched.isoformat() if self.timestamp_fetched else None,
            "status": self.status.value if self.status else None,
            "score": self.score,
            "label": self.label.value if self.label else None,
            "keywords_matched": self.keywords_matched,
            "llm_reasoning": self.llm_reasoning,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Resume(Base):
    """Resume model - ONLY ONE resume allowed at a time."""
    
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content = Column(Text, nullable=False)
    
    # Parsed data
    skills = Column(JSON)  # List of skills
    experiences = Column(JSON)  # List of experiences
    education = Column(JSON)  # List of education entries
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "content": self.content,
            "skills": self.skills,
            "experiences": self.experiences,
            "education": self.education,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
