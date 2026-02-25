from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import grants, organizations, tenants, funnel

app = FastAPI(title="Grant Funnel", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(organizations.router, prefix="/api/organizations", tags=["organizations"])
app.include_router(grants.router, prefix="/api/grants", tags=["grants"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["tenants"])
app.include_router(funnel.router, prefix="/api/tenants/{tenant_id}/funnel", tags=["funnel"])


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
