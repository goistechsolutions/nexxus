"""Tenant RLS policies."""
from alembic import op
revision="0002";down_revision="0001";branch_labels=None;depends_on=None
TABLES=("users","roles","documents","audit_events")
def upgrade():
 for table in TABLES:
  op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
  op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
  policy=f"CREATE POLICY {table}_tenant_isolation ON {table} USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
  op.execute(policy)
def downgrade():
 for table in reversed(TABLES):
  op.execute(f"DROP POLICY IF EXISTS {table}_tenant_isolation ON {table}")
  op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
