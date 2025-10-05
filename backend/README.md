# Job Monitoring Backend

FastAPI-based backend for the Job Monitoring & Resume Fit Agent.

## 🏗️ Architecture

```
main.py                      # FastAPI application entry point
│
├── api/                     # API layer
│   ├── routes.py           # REST endpoints
│   └── websocket_manager.py # WebSocket connections
│
├── services/                # Business logic
│   ├── job_fetcher.py      # Fetch jobs from sources
│   ├── job_normalizer.py   # Normalize job data
│   ├── resume_parser.py    # Parse resumes
│   ├── job_scorer.py       # Score jobs vs resume
│   ├── job_classifier.py   # Classify by score
│   └── embeddings.py       # Generate embeddings
│
├── pipeline/                # Orchestration
│   └── langgraph_pipeline.py # LangGraph state machine
│
├── models.py                # SQLAlchemy models
├── schemas.py               # Pydantic schemas
├── database.py              # Database setup
├── config.py                # Configuration
├── scheduler.py             # APScheduler jobs
└── utils/                   # Utilities
    └── logger.py           # Logging
```

## 🚀 Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp env_example.txt .env
# Edit .env with your settings

# Run
python main.py
```

## 📦 Dependencies

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **sqlalchemy**: ORM
- **pydantic**: Data validation
- **apscheduler**: Task scheduling
- **langchain/langgraph**: Orchestration
- **sentence-transformers**: Local embeddings
- **openai**: Optional cloud embeddings
- **pypdf2**: PDF parsing
- **scikit-learn**: Cosine similarity
- **pytest**: Testing

## 🔌 API Endpoints

### Jobs
```
GET  /api/jobs              # List jobs with filters
GET  /api/jobs/{id}         # Get specific job
GET  /api/jobs/stats/summary # Get statistics
```

### Resume
```
POST /api/resume/upload     # Upload resume
GET  /api/resume/active     # Get active resume
```

### Admin
```
POST /api/trigger-fetch     # Manual job fetch
WS   /api/ws               # WebSocket connection
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_job_scorer.py

# Run with coverage
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

## ⚙️ Configuration

Edit `.env`:

```env
# OpenAI API (optional)
OPENAI_API_KEY=sk-...

# Database
DATABASE_URL=sqlite:///./jobs.db

# Server
HOST=0.0.0.0
PORT=8000

# Scheduler
JOB_FETCH_INTERVAL_MINUTES=5

# Mock mode
USE_MOCK_DATA=true
```

## 📊 Database Schema

### Job Model
- job_id (unique)
- title, company, description
- location, type, apply_url
- status (pending/normalized/scored/classified)
- score (0-100)
- label (best/mid/least)
- embedding (JSON)
- keywords_matched (JSON)

### Resume Model
- filename, content
- skills, experiences, education (JSON)
- embedding (JSON)
- is_active (boolean)

## 🔄 Pipeline Flow

1. **Fetch**: Get jobs from sources
2. **Normalize**: Standardize data format
3. **Embed**: Generate job embedding
4. **Score**: Compare with resume (cosine similarity + keywords)
5. **Classify**: Categorize by threshold
6. **Store**: Save to database
7. **Broadcast**: Notify WebSocket clients

## 📝 Logging

Logs are written to:
- Console (stdout)
- `logs/app.log`

Log levels:
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Errors that need attention

## 🔍 Monitoring

Check application health:
```bash
curl http://localhost:8000/api/
```

View API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🛠️ Development

### Add a new service

1. Create file in `services/`
2. Implement service class
3. Add to `services/__init__.py`
4. Write tests in `tests/`

### Modify scoring algorithm

Edit `services/job_scorer.py`:
```python
def score_job(job_data, resume_data, job_embedding=None):
    # Your custom scoring logic here
    pass
```

### Add new API endpoint

Edit `api/routes.py`:
```python
@router.get("/api/your-endpoint")
async def your_endpoint(db: Session = Depends(get_db)):
    # Your logic here
    pass
```

## 🐛 Common Issues

### ImportError
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database locked
```bash
# Delete database and restart
rm jobs.db
python main.py
```

### Port already in use
```bash
# Change port in .env
PORT=8001
```

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)

