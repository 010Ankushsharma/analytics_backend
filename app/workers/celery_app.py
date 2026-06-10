"""Celery application with periodic tasks for cache/view refresh."""
from celery import Celery
from celery.schedules import crontab
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "analytics_worker",
    broker=settings.celery_broker_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "refresh-materialized-views": {
            "task": "app.workers.celery_app.refresh_views_task",
            "schedule": 300.0,
        },
        "warm-analytics-cache": {
            "task": "app.workers.celery_app.warm_cache_task",
            "schedule": 240.0,
        },
    },
)


@celery_app.task(name="app.workers.celery_app.refresh_views_task")
def refresh_views_task():
    """Refresh all materialized views."""
    from app.db.database import SessionLocal
    from app.db.materialized_views import refresh_materialized_views

    db = SessionLocal()
    try:
        refresh_materialized_views(db)
        return {"status": "success", "message": "Views refreshed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task(name="app.workers.celery_app.warm_cache_task")
def warm_cache_task():
    """Pre-warm analytics cache."""
    from app.db.database import SessionLocal
    from app.services.cache_service import CacheService
    from app.services.analytics_service import AnalyticsService

    db = SessionLocal()
    cache = CacheService()
    service = AnalyticsService(db=db, cache=cache)

    try:
        cache.flush_analytics()
        service.get_total_orders()
        service.get_total_revenue()
        service.get_total_refunds()
        service.get_net_revenue()
        service.get_average_order_value()
        service.get_repeat_customer_revenue()
        service.get_revenue_trends("daily")
        service.get_revenue_trends("weekly")
        service.get_revenue_trends("monthly")
        service.get_top_customers()
        return {"status": "success", "message": "Cache warmed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()