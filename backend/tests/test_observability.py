from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_response_returns_correlation_headers() -> None:
    response = client.get(
        "/v1/health/live",
        headers={
            "X-Request-Id": "test-request-id",
            "X-Trace-Id": "test-trace-id",
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Request-Id"] == "test-request-id"
    assert response.headers["X-Trace-Id"] == "test-trace-id"
    assert "X-Response-Time-Ms" in response.headers


def test_invalid_correlation_ids_are_replaced() -> None:
    response = client.get(
        "/v1/health/live",
        headers={
            "X-Request-Id": "invalid id with spaces",
            "X-Trace-Id": "invalid/trace/id",
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Request-Id"] != "invalid id with spaces"
    assert response.headers["X-Trace-Id"] != "invalid/trace/id"
