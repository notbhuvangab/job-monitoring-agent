"""Tests for JobSpy-based job fetcher."""
import pytest
from services.job_fetcher import JobFetcher


@pytest.mark.asyncio
async def test_job_fetcher_initialization():
    """Test job fetcher initializes with config."""
    fetcher = JobFetcher()
    
    assert fetcher.sources is not None
    assert fetcher.search_term is not None
    assert fetcher.results_wanted > 0


@pytest.mark.asyncio
async def test_fetch_returns_raw_records(monkeypatch):
    """Fetch should return raw JobSpy records; normalization handled later."""
    fetcher = JobFetcher()

    class DummyDF:
        def __init__(self, records):
            self._records = records
            self.empty = False
        def to_dict(self, orient):
            assert orient == 'records'
            return self._records

    def fake_scrape_jobs(**kwargs):
        return DummyDF([
            {'site': 'indeed', 'id': '1', 'title': 'A', 'company': 'C', 'job_url': 'u1'},
            {'site': 'linkedin', 'id': '2', 'title': 'B', 'company': 'D', 'job_url': 'u2'}
        ])

    monkeypatch.setattr('services.job_fetcher.scrape_jobs', fake_scrape_jobs)

    records = await fetcher.fetch_jobs()

    assert isinstance(records, list)
    assert len(records) == 2
    assert records[0]['site'] == 'indeed'


def test_no_internal_type_detection_anymore():
    """Ensure internal type detection helper is removed."""
    fetcher = JobFetcher()
    assert not hasattr(fetcher, '_normalize_job')
