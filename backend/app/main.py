from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.router import router

app = FastAPI(
    title="YottaFlex Employee Lifecycle Orchestrator API",
    description="Enterprise workflow coordinator for onboarding, offboarding, access, assets, dependencies, and auditability.",
    version="2.0.0",
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "system": "YottaFlex Employee Lifecycle Orchestrator",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "status": "operational",
    }
