import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

client = TestClient(app)


@pytest.fixture
def mock_redis():
    with patch('main.get_redis') as mock:
        r = MagicMock()
        mock.return_value = r
        yield r


def test_create_job(mock_redis):
    """POST /jobs should create a job, push to queue and return a job_id"""
    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36  # UUID format
    mock_redis.lpush.assert_called_once()
    mock_redis.hset.assert_called_once()


def test_get_job_found(mock_redis):
    """GET /jobs/:id should return job_id and status when job exists"""
    mock_redis.hget.return_value = "queued"
    response = client.get("/jobs/test-job-123")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-123"
    assert data["status"] == "queued"


def test_get_job_not_found(mock_redis):
    """GET /jobs/:id should return 404 when job does not exist"""
    mock_redis.hget.return_value = None
    response = client.get("/jobs/nonexistent-job")
    assert response.status_code == 404
    assert response.json()["detail"] == "job not found"


def test_get_job_completed(mock_redis):
    """GET /jobs/:id should return completed status after job is processed"""
    mock_redis.hget.return_value = "completed"
    response = client.get("/jobs/completed-job-123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_health_ok(mock_redis):
    """GET /health should return 200 when Redis is reachable"""
    mock_redis.ping.return_value = True
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_redis_down():
    """GET /health should return 503 when Redis is unavailable"""
    with patch('main.get_redis') as mock:
        mock.return_value.ping.side_effect = Exception("Redis unavailable")
        response = client.get("/health")
        assert response.status_code == 503
        assert response.json()["detail"] == "redis unavailable"
