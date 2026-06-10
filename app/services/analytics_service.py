"""Analytics business logic service layer."""
from sqlalchemy.orm import Session
from app.repositories.order_repository import OrderRepository
from app.repositories.refund_repository import RefundRepository
from app.services.cache_service import CacheService
from app.schemas.schemas import (
    AnalyticsMetric,
    RevenueTrendResponse,
    RevenueTrendItem,
    TopCustomersResponse,
    TopCustomerItem,
)
from datetime import datetime
from typing import Optional


class AnalyticsService:
    """Service containing analytics business logic with caching."""

    def __init__(self, db: Session, cache: CacheService):
        self.order_repo = OrderRepository(db)
        self.refund_repo = RefundRepository(db)
        self.cache = cache

    def _get_cached_or_compute(self, cache_key: str, compute_fn) -> tuple:
        """Check cache first, compute if miss. Returns (value, cached_flag)."""
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached, True
        
        value = compute_fn()
        self.cache.set(cache_key, value)
        return value, False

    def get_total_orders(self) -> AnalyticsMetric:
        """Total number of orders."""
        value, cached = self._get_cached_or_compute(
            "analytics:total_orders",
            lambda: self.order_repo.count()
        )
        return AnalyticsMetric(
            metric="total_orders", value=float(value), cached=cached
        )

    def get_total_revenue(self) -> AnalyticsMetric:
        """Total revenue from completed orders."""
        value, cached = self._get_cached_or_compute(
            "analytics:total_revenue",
            lambda: self.order_repo.get_total_revenue()
        )
        return AnalyticsMetric(
            metric="total_revenue", value=float(value), cached=cached
        )

    def get_total_refunds(self) -> AnalyticsMetric:
        """Total refund amount."""
        value, cached = self._get_cached_or_compute(
            "analytics:total_refunds",
            lambda: self.refund_repo.get_total_refunds()
        )
        return AnalyticsMetric(
            metric="total_refunds", value=float(value), cached=cached
        )

    def get_net_revenue(self) -> AnalyticsMetric:
        """Net revenue = total revenue - total refunds."""
        revenue_val, _ = self._get_cached_or_compute(
            "analytics:total_revenue",
            lambda: self.order_repo.get_total_revenue()
        )
        refund_val, _ = self._get_cached_or_compute(
            "analytics:total_refunds",
            lambda: self.refund_repo.get_total_refunds()
        )
        net = float(revenue_val) - float(refund_val)
        return AnalyticsMetric(metric="net_revenue", value=net, cached=False)

    def get_average_order_value(self) -> AnalyticsMetric:
        """Average order value."""
        value, cached = self._get_cached_or_compute(
            "analytics:avg_order_value",
            lambda: self.order_repo.get_average_order_value()
        )
        return AnalyticsMetric(
            metric="average_order_value", value=float(value), cached=cached
        )

    def get_repeat_customer_revenue(self) -> AnalyticsMetric:
        """Revenue from customers with more than one order."""
        value, cached = self._get_cached_or_compute(
            "analytics:repeat_customer_revenue",
            lambda: self.order_repo.get_repeat_customer_revenue()
        )
        return AnalyticsMetric(
            metric="repeat_customer_revenue", value=float(value), cached=cached
        )

    def get_revenue_trends(self, period: str = "daily") -> RevenueTrendResponse:
        """Revenue trends by period."""
        cache_key = f"analytics:revenue_trends:{period}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            return RevenueTrendResponse(
                period_type=period,
                data=[RevenueTrendItem(**item) for item in cached_data],
                cached=True,
            )
        
        if period == "daily":
            raw_data = self.order_repo.get_revenue_trends_daily()
        elif period == "weekly":
            raw_data = self.order_repo.get_revenue_trends_weekly()
        else:
            raw_data = self.order_repo.get_revenue_trends_monthly()
        
        # Cache the raw data
        self.cache.set(cache_key, raw_data)
        
        return RevenueTrendResponse(
            period_type=period,
            data=[RevenueTrendItem(**item) for item in raw_data],
            cached=False,
        )

    def get_top_customers(self, limit: int = 10) -> TopCustomersResponse:
        """Top customers by total spend."""
        cache_key = f"analytics:top_customers:{limit}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            return TopCustomersResponse(
                data=[TopCustomerItem(**item) for item in cached_data],
                cached=True,
            )
        
        raw_data = self.order_repo.get_top_customers(limit)
        self.cache.set(cache_key, raw_data)
        
        return TopCustomersResponse(
            data=[TopCustomerItem(**item) for item in raw_data],
            cached=False,
        )