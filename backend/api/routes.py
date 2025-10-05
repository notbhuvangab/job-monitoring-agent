"""API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from database import get_db
from models import Job, Resume, JobStatus, JobLabel
from schemas import JobResponse, ResumeResponse
from services import ResumeParser
from api.websocket_manager import manager
from utils import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Job Monitoring & Resume Fit Agent API",
        "version": "1.0.0"
    }


@router.get("/jobs", response_model=List[JobResponse])
async def get_jobs(
    label: Optional[JobLabel] = Query(None, description="Filter by job label (best/mid/least)"),
    company: Optional[str] = Query(None, description="Filter by company name"),
    remote_only: bool = Query(False, description="Show only remote jobs"),
    search: Optional[str] = Query(None, description="Search in title or description"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of jobs to return"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip"),
    db: Session = Depends(get_db)
):
    """
    Get jobs with optional filtering.
    
    - **label**: Filter by fit category (best, mid, least)
    - **company**: Filter by company name (partial match)
    - **remote_only**: Show only remote positions
    - **search**: Search term for title or description
    - **limit**: Maximum results to return
    - **offset**: Pagination offset
    """
    query = db.query(Job).filter(Job.status == JobStatus.CLASSIFIED)
    
    # Apply filters
    if label:
        query = query.filter(Job.label == label)
    
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    
    if remote_only:
        query = query.filter(Job.type == "remote")
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Job.title.ilike(search_term),
                Job.description.ilike(search_term),
                Job.company.ilike(search_term)
            )
        )
    
    # Order by score (descending) and limit
    jobs = query.order_by(Job.score.desc()).offset(offset).limit(limit).all()
    
    logger.info(f"Retrieved {len(jobs)} jobs with filters: label={label}, company={company}, remote_only={remote_only}, search={search}")
    
    return jobs


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.get("/jobs/stats/summary")
async def get_stats(db: Session = Depends(get_db)):
    """Get statistics summary of jobs."""
    total_jobs = db.query(Job).count()
    classified_jobs = db.query(Job).filter(Job.status == JobStatus.CLASSIFIED).count()
    
    best_fit = db.query(Job).filter(Job.label == JobLabel.BEST_FIT).count()
    mid_fit = db.query(Job).filter(Job.label == JobLabel.MID_FIT).count()
    least_fit = db.query(Job).filter(Job.label == JobLabel.LEAST_FIT).count()
    
    remote_jobs = db.query(Job).filter(Job.type == "remote").count()
    hybrid_jobs = db.query(Job).filter(Job.type == "hybrid").count()
    onsite_jobs = db.query(Job).filter(Job.type == "onsite").count()
    
    return {
        "total_jobs": total_jobs,
        "classified_jobs": classified_jobs,
        "by_label": {
            "best_fit": best_fit,
            "mid_fit": mid_fit,
            "least_fit": least_fit
        },
        "by_type": {
            "remote": remote_jobs,
            "hybrid": hybrid_jobs,
            "onsite": onsite_jobs
        }
    }


@router.post("/resume/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse a resume (PDF or text).
    Only ONE resume is allowed - uploading a new one replaces the existing one.
    """
    try:
        content = await file.read()
        
        # Parse based on file type
        if file.filename.endswith('.pdf'):
            text = ResumeParser.parse_pdf(content)
        else:
            text = content.decode('utf-8')
        
        # Parse resume
        parsed_data = ResumeParser.parse_text(text)
        
        # DELETE all existing resumes (only one allowed)
        db.query(Resume).delete()
        
        # Create new resume entry (no embedding, no is_active)
        resume = Resume(
            filename=file.filename,
            content=parsed_data["content"],
            skills=parsed_data["skills"],
            experiences=parsed_data["experiences"],
            education=parsed_data["education"]
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        logger.info(f"Uploaded and parsed resume: {file.filename}")
        logger.info(f"  - Skills: {len(parsed_data['skills'])}")
        logger.info(f"  - Experiences: {len(parsed_data['experiences'])}")
        logger.info(f"  - Education: {len(parsed_data['education'])}")
        
        return resume
        
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing resume: {str(e)}")


@router.get("/resume/current", response_model=ResumeResponse)
async def get_current_resume(db: Session = Depends(get_db)):
    """Get the current resume (only one allowed)."""
    resume = db.query(Resume).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found. Please upload a resume first.")
    
    return resume


@router.delete("/resume/delete")
async def delete_resume(db: Session = Depends(get_db)):
    """Delete the current resume."""
    deleted_count = db.query(Resume).delete()
    db.commit()
    
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="No resume found to delete.")
    
    logger.info("Resume deleted")
    return {"message": "Resume deleted successfully"}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time job updates.
    
    Clients can connect to this endpoint to receive real-time notifications
    when new jobs are processed and classified.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive and wait for messages
            data = await websocket.receive_text()
            
            # Echo back for heartbeat
            await manager.send_personal_message(
                {"type": "heartbeat", "message": "pong"},
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")

