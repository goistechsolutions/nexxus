from datetime import datetime,timedelta,timezone
from hashlib import sha256
from secrets import token_urlsafe
from uuid import UUID
import jwt
from pwdlib import PasswordHash
from app.core.config import get_settings
ph=PasswordHash.recommended()
def hash_password(v:str)->str:return ph.hash(v)
def verify_password(v:str,h:str)->bool:return ph.verify(v,h)
def hash_jti(jti:str)->str:return sha256(jti.encode()).hexdigest()
def issue_token(subject:UUID,tenant_id:UUID,token_version:int,kind:str,minutes:int,permissions:list[str]|None=None,jti:str|None=None)->str:
 s=get_settings();now=datetime.now(timezone.utc);claims={"sub":str(subject),"tenant_id":str(tenant_id),"ver":token_version,"type":kind,"iat":now,"exp":now+timedelta(minutes=minutes)}
 if permissions is not None: claims["permissions"]=permissions
 if jti is not None: claims["jti"]=jti
 return jwt.encode(claims,s.jwt_secret,algorithm=s.jwt_algorithm)
def create_access_token(uid:UUID,tid:UUID,ver:int,permissions:list[str])->str:return issue_token(uid,tid,ver,"access",15,permissions)
def create_refresh_token(uid:UUID,tid:UUID,ver:int)->tuple[str,str,datetime]:
 jti=token_urlsafe(32);expires=datetime.now(timezone.utc)+timedelta(days=7);return issue_token(uid,tid,ver,"refresh",7*24*60,jti=jti),jti,expires
def decode_token(token:str,kind:str)->dict:
 s=get_settings();claims=jwt.decode(token,s.jwt_secret,algorithms=[s.jwt_algorithm],options={"require":["sub","tenant_id","type","ver","iat","exp"]})
 if claims["type"]!=kind:raise jwt.InvalidTokenError("wrong token type")
 return claims
