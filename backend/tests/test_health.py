import os
os.environ.setdefault("NEXXUS_JWT_SECRET","test-secret-that-is-at-least-32-characters-long")
from fastapi.testclient import TestClient
from app.main import app
def test_live():
 with TestClient(app) as client:
  r=client.get("/health/live",headers={"host":"localhost"});assert r.status_code==200;assert r.json()=={"status":"ok"}
