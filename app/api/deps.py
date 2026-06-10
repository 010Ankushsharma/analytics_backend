"""Dependency injection for API routes."""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.cache_service import CacheService, get_cache_service
from app.services.analytics_service import AnalyticsService


def get_analytics_service(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
) -> AnalyticsService:
    """Dependency injection for AnalyticsService."""
    return AnalyticsService(db=db, cache=cache)