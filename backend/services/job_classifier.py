"""Job classification service."""
from typing import Dict, Any
from models import JobLabel
from utils import get_logger

logger = get_logger(__name__)


class JobClassifier:
    """Classify jobs into categories based on scores."""
    
    # Score thresholds
    BEST_FIT_THRESHOLD = 85
    MID_FIT_THRESHOLD = 65
    
    @staticmethod
    def classify(score: float) -> JobLabel:
        """
        Classify job based on score.
        
        Args:
            score: Job score (0-100)
        
        Returns:
            JobLabel enum value
        """
        if score >= JobClassifier.BEST_FIT_THRESHOLD:
            label = JobLabel.BEST_FIT
        elif score >= JobClassifier.MID_FIT_THRESHOLD:
            label = JobLabel.MID_FIT
        else:
            label = JobLabel.LEAST_FIT
        
        logger.debug(f"Classified job with score {score} as {label.value}")
        return label
    
    # Note: batch_classify was removed as unused to reduce surface area

