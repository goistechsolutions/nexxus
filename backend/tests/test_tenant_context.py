from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_tenant_context_requires_header() -> None:
    response = client.get("/v1/tenants/context")

    assert response.status_code == 400


def test_tenant_context_rejects_invalid_uuid() -> None:
    response = client.get("/v1/tenants/context", headers={"X-Tenant-Id": "invalid"})

    assert response.status_code == 400


def test_tenant_context_accepts_uuid() -> None:
    tenant_id = uuid4()

    response = client.get(
        "/v1/tenants/context", headers={"X-Tenant-Id": str(tenant_id)}
    )

    assert response.status_code == 200
    assert response.json() == {"tenant_id": str(tenant_id)}
