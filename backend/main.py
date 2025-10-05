"""Main FastAPI application."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import get_settings
from database import init_db, SessionLocal
from api import router
from scheduler import JobScheduler
from utils import get_logger
from fastapi import HTTPException
from models import Resume

logger = get_logger(__name__)
settings = get_settings()

# Initialize scheduler
job_scheduler = JobScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Job Monitoring & Resume Fit Agent")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Start scheduler
    job_scheduler.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    job_scheduler.stop()


# Create FastAPI app
app = FastAPI(
    title="Job Monitoring & Resume Fit Agent",
    description="AI-powered job matching system with real-time monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Job Monitoring & Resume Fit Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/api/trigger-fetch")
async def trigger_fetch():
    """Manually trigger job fetch (for testing)."""
    # Check if resume exists

    
    db = SessionLocal()
    try:
        resume = db.query(Resume).first()
        if not resume:
            raise HTTPException(
                status_code=400, 
                detail="Please upload a resume first before fetching jobs."
            )
    finally:
        db.close()
    
    await job_scheduler.run_now()
    return {"message": "Job fetch triggered"}


@app.get("/api/scheduler/info")
async def get_scheduler_info():
    """Get scheduler information including fetch times."""
    return {
        "is_running": job_scheduler.is_running,
        "last_fetch": job_scheduler.last_fetch_time.isoformat() if job_scheduler.last_fetch_time else None,
        "next_fetch": job_scheduler.next_fetch_time.isoformat() if job_scheduler.next_fetch_time else None,
        "fetch_interval_minutes": job_scheduler.fetch_interval_minutes
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )

