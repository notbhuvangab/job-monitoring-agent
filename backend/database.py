"""Database setup and session management."""
from config import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

settings = get_settings()

# Create engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from models import Job, Resume  # Import here to avoid circular imports
    Base.metadata.create_all(bind=engine)
