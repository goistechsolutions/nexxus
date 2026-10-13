import os
from uuid import uuid4

import jwt
import pytest

os.environ.setdefault(
    "NEXXUS_JWT_SECRET",
    "test-secret-that-is-at-least-32-characters-long",
)

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_jti,
)


def test_access_token_contains_expected_claims() -> None:
    user_id = uuid4()
    tenant_id = uuid4()

    token = create_access_token(
        user_id,
        tenant_id,
        token_version=2,
        permissions=["users:read"],
        expires_in_minutes=2,
    )
    claims = decode_token(token, "access", expected_token_version=2)

    assert claims["sub"] == str(user_id)
    assert claims["tenant_id"] == str(tenant_id)
    assert claims["permissions"] == ["users:read"]
    assert claims["token_type"] == "access"
    assert claims["ver"] == 2


def test_refresh_token_returns_jti_and_expiry() -> None:
    token, jti, expires_at = create_refresh_token(
        uuid4(),
        uuid4(),
        token_version=1,
        expires_in_days=1,
    )
    claims = decode_token(token, "refresh", expected_token_version=1)

    assert claims["token_type"] == "refresh"
    assert claims["jti"] == jti
    assert claims["ver"] == 1
    assert expires_at.tzinfo is not None


def test_decode_token_rejects_wrong_token_type() -> None:
    token = create_access_token(uuid4(), uuid4(), token_version=1)

    with pytest.raises(ValueError):
        decode_token(token, "refresh")


def test_decode_token_rejects_invalid_signature() -> None:
    forged = jwt.encode(
        {
            "sub": str(uuid4()),
            "tenant_id": str(uuid4()),
            "token_type": "access",
            "ver": 1,
        },
        "another-secret",
        algorithm="HS256",
    )

    with pytest.raises(ValueError):
        decode_token(forged, "access")


def test_decode_token_rejects_old_token_version() -> None:
    token = create_access_token(uuid4(), uuid4(), token_version=1)

    with pytest.raises(ValueError):
        decode_token(token, "access", expected_token_version=2)


def test_hash_jti_is_deterministic_and_non_reversible() -> None:
    assert hash_jti("test-jti") == hash_jti("test-jti")
    assert hash_jti("test-jti") != "test-jti"
