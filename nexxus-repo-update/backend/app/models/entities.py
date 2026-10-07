from datetime import datetime
from uuid import UUID
from sqlalchemy import Boolean,DateTime,ForeignKey,String,Table,Column,Text,UniqueConstraint,JSON,func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped,mapped_column,relationship
from pgvector.sqlalchemy import Vector
from app.models.base import Base,UUIDPK,Timestamped
user_roles=Table("user_roles",Base.metadata,Column("user_id",PGUUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),primary_key=True),Column("role_id",PGUUID(as_uuid=True),ForeignKey("roles.id",ondelete="CASCADE"),primary_key=True))
role_permissions=Table("role_permissions",Base.metadata,Column("role_id",PGUUID(as_uuid=True),ForeignKey("roles.id",ondelete="CASCADE"),primary_key=True),Column("permission_id",PGUUID(as_uuid=True),ForeignKey("permissions.id",ondelete="CASCADE"),primary_key=True))
class Tenant(UUIDPK,Timestamped,Base):
 __tablename__="tenants";slug:Mapped[str]=mapped_column(String(80),unique=True,index=True);name:Mapped[str]=mapped_column(String(200));active:Mapped[bool]=mapped_column(Boolean,default=True)
class User(UUIDPK,Timestamped,Base):
 __tablename__="users";tenant_id:Mapped[UUID]=mapped_column(ForeignKey("tenants.id",ondelete="CASCADE"),index=True);email:Mapped[str]=mapped_column(String(320));password_hash:Mapped[str]=mapped_column(String(500));active:Mapped[bool]=mapped_column(Boolean,default=True);token_version:Mapped[int]=mapped_column(default=0);roles:Mapped[list["Role"]]=relationship(secondary=user_roles,lazy="selectin");__table_args__=(UniqueConstraint("tenant_id","email",name="uq_users_tenant_email"),)
class Role(UUIDPK,Timestamped,Base):
 __tablename__="roles";tenant_id:Mapped[UUID]=mapped_column(ForeignKey("tenants.id",ondelete="CASCADE"),index=True);name:Mapped[str]=mapped_column(String(80));permissions:Mapped[list["Permission"]]=relationship(secondary=role_permissions,lazy="selectin");__table_args__=(UniqueConstraint("tenant_id","name",name="uq_roles_tenant_name"),)
class Permission(UUIDPK,Base):
 __tablename__="permissions";code:Mapped[str]=mapped_column(String(100),unique=True);description:Mapped[str]=mapped_column(String(250))
class RefreshToken(UUIDPK,Base):
 __tablename__="refresh_tokens";user_id:Mapped[UUID]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True);tenant_id:Mapped[UUID]=mapped_column(ForeignKey("tenants.id",ondelete="CASCADE"),index=True);jti_hash:Mapped[str]=mapped_column(String(64),unique=True,index=True);expires_at:Mapped[datetime]=mapped_column(DateTime(timezone=True));revoked_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True));created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class Document(UUIDPK,Timestamped,Base):
 __tablename__="documents";tenant_id:Mapped[UUID]=mapped_column(ForeignKey("tenants.id",ondelete="CASCADE"),index=True);title:Mapped[str]=mapped_column(String(250));content:Mapped[str]=mapped_column(Text);metadata_json:Mapped[dict]=mapped_column("metadata",JSON,default=dict);embedding:Mapped[list[float]|None]=mapped_column(Vector(1536),nullable=True)
class AuditEvent(UUIDPK,Base):
 __tablename__="audit_events";tenant_id:Mapped[UUID]=mapped_column(ForeignKey("tenants.id",ondelete="RESTRICT"),index=True);actor_id:Mapped[UUID|None]=mapped_column(ForeignKey("users.id",ondelete="SET NULL"));action:Mapped[str]=mapped_column(String(120),index=True);resource:Mapped[str]=mapped_column(String(250));details:Mapped[dict]=mapped_column(JSON,default=dict);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
