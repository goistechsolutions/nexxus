from pydantic import BaseModel,EmailStr,Field
class BootstrapRequest(BaseModel):tenant_slug:str=Field(pattern=r"^[a-z0-9-]+$");tenant_name:str;admin_email:EmailStr;admin_password:str=Field(min_length=12)
class RoleCreate(BaseModel):name:str=Field(min_length=2,max_length=80);permissions:list[str]
class UserCreate(BaseModel):email:EmailStr;password:str=Field(min_length=12);roles:list[str]=[]
