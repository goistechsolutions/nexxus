"""Authentication lifecycle and RBAC seed."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0003";down_revision="0002";branch_labels=None;depends_on=None
PERMS=(("users:read","Read users"),("users:write","Manage users"),("roles:read","Read roles"),("roles:write","Manage roles"),("documents:read","Read documents"),("documents:write","Manage documents"),("audit:read","Read audit events"))
def upgrade():
 op.add_column("users",sa.Column("token_version",sa.Integer(),nullable=False,server_default="0"))
 op.create_table("refresh_tokens",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("user_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("tenant_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("tenants.id",ondelete="CASCADE"),nullable=False),sa.Column("jti_hash",sa.String(64),unique=True,nullable=False),sa.Column("expires_at",sa.DateTime(timezone=True),nullable=False),sa.Column("revoked_at",sa.DateTime(timezone=True)),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
 op.create_index("ix_refresh_tokens_jti_hash","refresh_tokens",["jti_hash"]);op.create_index("ix_refresh_tokens_tenant_id","refresh_tokens",["tenant_id"])
 op.execute("ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY");op.execute("ALTER TABLE refresh_tokens FORCE ROW LEVEL SECURITY")
 op.execute("CREATE POLICY refresh_tokens_tenant_isolation ON refresh_tokens USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)")
 table=sa.table("permissions",sa.column("id",postgresql.UUID),sa.column("code",sa.String),sa.column("description",sa.String))
 from uuid import uuid4
 op.bulk_insert(table,[{"id":uuid4(),"code":c,"description":d} for c,d in PERMS])
def downgrade():
 op.drop_table("refresh_tokens");op.drop_column("users","token_version")
 for code,_ in PERMS:op.execute(sa.text("DELETE FROM permissions WHERE code=:c").bindparams(c=code))
