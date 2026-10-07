from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env",env_prefix="NEXXUS_",extra="ignore")
    app_name:str="Nexxus API"; env:str="development"
    database_url:str="postgresql+asyncpg://nexxus:change-me@127.0.0.1:5432/nexxus"
    jwt_secret:str=Field(min_length=32); jwt_algorithm:str="HS256"; access_token_minutes:int=15
    allowed_hosts:list[str]=["localhost","127.0.0.1"]; cors_origins:list[str]=[]
    @field_validator("jwt_secret")
    @classmethod
    def reject_default(cls,v:str)->str:
        if v.startswith("change-"): raise ValueError("configure NEXXUS_JWT_SECRET")
        return v
@lru_cache
def get_settings()->Settings: return Settings()
