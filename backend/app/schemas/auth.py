from pydantic import BaseModel,EmailStr,Field
class LoginRequest(BaseModel):tenant:str=Field(min_length=2,max_length=80);email:EmailStr;password:str=Field(min_length=12,max_length=256)
class RefreshRequest(BaseModel):refresh_token:str
class LogoutRequest(BaseModel):refresh_token:str
class TokenPair(BaseModel):access_token:str;refresh_token:str;token_type:str="bearer";expires_in:int=900
