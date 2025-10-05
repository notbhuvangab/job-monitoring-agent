"""LangGraph pipeline - simplified following best practices."""
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, START, END
from utils import get_logger
from services import JobNormalizer, JobScorer, JobClassifier

logger = get_logger(__name__)


class PipelineState(TypedDict):
    """State for job processing pipeline."""
    raw_job: Dict[str, Any]
    normalized_job: Dict[str, Any]
    resume_data: Dict[str, Any]
    score: float
    score_details: Dict[str, Any]
    label: str
    error: str
    job_id: str


def normalize_job(state: PipelineState) -> Dict[str, Any]:
    """Normalize raw job data."""
    try:
        normalized = JobNormalizer.normalize(state["raw_job"])
        if not normalized:
            return {"error": "Failed to normalize job"}
        
        logger.debug(f"Normalized job: {normalized['job_id']}")
        return {
            "normalized_job": normalized,
            "job_id": normalized["job_id"]
        }
    except Exception as e:
        logger.error(f"Normalize error: {e}")
        return {"error": str(e)}


def score_job(state: PipelineState) -> Dict[str, Any]:
    """Score job against resume using LLM."""
    if state.get("error"):
        return {}
    
    try:
        score, details = JobScorer.score_job(
            state["normalized_job"],
            state["resume_data"]
        )
        
        logger.debug(f"Scored job {state['job_id']}: {score}/100")
        return {
            "score": score,
            "score_details": details
        }
    except Exception as e:
        logger.error(f"Score error: {e}")
        return {"error": str(e), "score": 0.0}


def classify_job(state: PipelineState) -> Dict[str, Any]:
    """Classify job based on score."""
    if state.get("error"):
        return {}
    
    try:
        label = JobClassifier.classify(state["score"])
        logger.debug(f"Classified job {state['job_id']} as {label.value}")
        return {"label": label.value}
    except Exception as e:
        logger.error(f"Classify error: {e}")
        return {"error": str(e)}


class JobProcessingPipeline:
    """LangGraph-based job processing pipeline."""
    
    def __init__(self):
        self.graph = build_graph()
    
    def process_job(self, raw_job: Dict[str, Any], resume_data: Dict[str, Any]) -> PipelineState:
        """Process a job through the pipeline."""
        initial_state: PipelineState = {
            "raw_job": raw_job,
            "resume_data": resume_data,
            "normalized_job": {},
            "score": 0.0,
            "score_details": {},
            "label": "",
            "error": "",
            "job_id": ""
        }
        
        try:
            return self.graph.invoke(initial_state)
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            initial_state["error"] = str(e)
            return initial_state

def build_graph():
    """Build the LangGraph pipeline."""
    builder = StateGraph(PipelineState)
    
    # Add nodes by function (LangGraph references them by function name)
    builder.add_node(normalize_job)
    builder.add_node(score_job)
    builder.add_node(classify_job)
    
    # Define edges - simple linear flow
    builder.add_edge(START, "normalize_job")
    builder.add_edge("normalize_job", "score_job")
    builder.add_edge("score_job", "classify_job")
    builder.add_edge("classify_job", END)
    
    return builder.compile()
# Create standalone graph instance for CLI
graph = build_graph()