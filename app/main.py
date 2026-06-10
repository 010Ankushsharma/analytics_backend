"""FastAPI application entry point."""
from fastapi import FastAPI
from app.api.routes import mock_data, analytics
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=(
        "A high-performance backend service for data ingestion and analytics. "
        "Ingests 100K customers, 1M orders, and 200K refunds, then exposes "
        "analytics endpoints with sub-2-second response times."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers
app.include_router(mock_data.router)
app.include_router(analytics.router)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}


@app.get("/", tags=["Root"])
def root():
    """Root endpoint with API information."""
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }