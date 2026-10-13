import os
from uuid import uuid4

import jwt
import pytest

os.environ.setdefault(
    "NEXXUS_JWT_SECRET",
    "test-secret-that-is-at-least-32-characters-long",
)

from app.core.security import (  # noqa: E402
    create_access_token,
    decode_token,
    hash_jti,
)


def test_access_token_contains_expected_claims() -> None:
    user_id = uuid4()
    tenant_id = uuid4()

    token = create_access_token(
        user_id,
        tenant_id,
        expires_in_minutes=2,
        permissions=["users:read"],
    )
    claims = decode_token(token, "access")

    assert claims["sub"] == str(user_id)
    assert claims["tenant_id"] == str(tenant_id)
    assert claims["permissions"] == ["users:read"]
    assert claims["token_type"] == "access"


def test_decode_token_rejects_wrong_token_type() -> None:
    token = create_access_token(uuid4(), uuid4())

    with pytest.raises(ValueError):
        decode_token(token, "refresh")


def test_decode_token_rejects_invalid_signature() -> None:
    token = create_access_token(uuid4(), uuid4())
    forged = jwt.encode(
        {"sub": str(uuid4()), "token_type": "access"},
        "another-secret",
        algorithm="HS256",
    )

    with pytest.raises(ValueError):
        decode_token(forged, "access")

    assert hash_jti("test-jti") != "test-jti"
