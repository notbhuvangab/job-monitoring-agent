"""Tests for job classifier service."""
from services.job_classifier import JobClassifier
from models import JobLabel


def test_classify_best_fit():
    """Test classification of best fit jobs."""
    label = JobClassifier.classify(90)
    assert label == JobLabel.BEST_FIT


def test_classify_mid_fit():
    """Test classification of mid fit jobs."""
    label = JobClassifier.classify(75)
    assert label == JobLabel.MID_FIT


def test_classify_least_fit():
    """Test classification of least fit jobs."""
    label = JobClassifier.classify(50)
    assert label == JobLabel.LEAST_FIT


def test_classify_boundaries():
    """Test classification at threshold boundaries."""
    assert JobClassifier.classify(85) == JobLabel.BEST_FIT
    assert JobClassifier.classify(84.9) == JobLabel.MID_FIT
    assert JobClassifier.classify(65) == JobLabel.MID_FIT
    assert JobClassifier.classify(64.9) == JobLabel.LEAST_FIT


def test_no_batch_classify():
    """Ensure removed batch_classify is not present."""
    assert not hasattr(JobClassifier, 'batch_classify')
