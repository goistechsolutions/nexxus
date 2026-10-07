from uuid import uuid4
import os
os.environ.setdefault("NEXXUS_JWT_SECRET","test-secret-that-is-at-least-32-characters-long")
from app.core.security import create_access_token,decode_token
def test_access_claims():
 uid,tid=uuid4(),uuid4();token=create_access_token(uid,tid,2,["users:read"]);claims=decode_token(token,"access");assert claims["sub"]==str(uid);assert claims["tenant_id"]==str(tid);assert claims["permissions"]==["users:read"]
