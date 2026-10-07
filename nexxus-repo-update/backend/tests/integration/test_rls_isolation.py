import pytest
pytestmark=pytest.mark.integration
@pytest.mark.skip(reason="Requires disposable PostgreSQL with pgvector and non-BYPASSRLS application role")
def test_cross_tenant_rows_are_invisible():
    # CI must provision two tenants, SET LOCAL each identity, and assert SELECT/INSERT isolation.
    raise AssertionError("replace skip with PostgreSQL fixture in CI")
