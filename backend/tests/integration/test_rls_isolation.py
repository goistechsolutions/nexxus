import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skip(
    reason=(
        "Requires disposable PostgreSQL with pgvector and "
        "non-BYPASSRLS application role"
    )
)
def test_cross_tenant_rows_are_invisible() -> None:
    """CI must provision two tenants and assert SELECT/INSERT isolation."""
    raise AssertionError("replace skip with PostgreSQL fixture in CI")
