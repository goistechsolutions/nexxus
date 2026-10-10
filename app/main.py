from uuid import uuid4
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.api.routes import admin,auth,context,health
from app.core.config import get_settings
s=get_settings();app=FastAPI(title=s.app_name,version="0.2.0",docs_url="/docs" if s.env!="production" else None)
app.add_middleware(TrustedHostMiddleware,allowed_hosts=s.allowed_hosts)
if s.cors_origins:app.add_middleware(CORSMiddleware,allow_origins=s.cors_origins,allow_credentials=True,allow_methods=["GET","POST","PUT","PATCH","DELETE"],allow_headers=["Authorization","Content-Type","X-Tenant-ID","X-Correlation-ID"])
@app.middleware("http")
async def correlation(request:Request,call_next):
 request.state.correlation_id=request.headers.get("X-Correlation-ID",str(uuid4()));response=await call_next(request);response.headers["X-Correlation-ID"]=request.state.correlation_id;return response
app.include_router(health.router,prefix="/health");app.include_router(auth.router,prefix="/api/v1");app.include_router(context.router,prefix="/api/v1");app.include_router(admin.router,prefix="/api/v1")
