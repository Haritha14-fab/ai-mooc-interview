"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.config import settings
from app.database import create_tables
from app.middleware.rate_limit import sensitive_endpoint_rate_limit
from app.routes import auth, subjects, assessments


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_tables()
    yield

# Initialize FastAPI app
app = FastAPI(
    title="AI MOOC Interview & Assessment System",
    description="An AI-powered technical assessment platform",
    version="1.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.middleware("http")(sensitive_endpoint_rate_limit)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[host.strip() for host in settings.ALLOWED_HOSTS.split(",") if host.strip()],
)


# Include routers
app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(assessments.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "AI MOOC Interview & Assessment System API",
        "version": app.version,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Basic service health check."""
    return {
        "status": "healthy",
        "service": "AI MOOC Interview System"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )
