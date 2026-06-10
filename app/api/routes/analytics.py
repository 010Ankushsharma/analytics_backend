"""Analytics API endpoints with caching."""
from fastapi import APIRouter, Depends, Query
from app.api.deps import get_analytics_service
from app.services.analytics_service import AnalyticsService
from app.schemas.schemas import (
    AnalyticsMetric,
    RevenueTrendResponse,
    TopCustomersResponse,
    TrendPeriod,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/total-orders",
    response_model=AnalyticsMetric,
    summary="Total number of orders",
    description="Returns the total count of all orders in the system.",
    responses={200: {"description": "Total order count", "content": {"application/json": {"example": {"metric": "total_orders", "value": 1000000, "cached": True, "computed_at": "2026-06-09T10:30:00Z"}}}}},
)
def total_orders(service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_total_orders()


@router.get(
    "/total-revenue",
    response_model=AnalyticsMetric,
    summary="Total revenue",
    description="Returns the sum of all completed order amounts.",
    responses={200: {"description": "Total revenue value"}},
)
def total_revenue(service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_total_revenue()


@router.get(
    "/total-refunds",
    response_model=AnalyticsMetric,
    summary="Total refund amount",
    description="Returns the sum of all refund amounts.",
)
def total_refunds(service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_total_refunds()


@router.get(
    "/net-revenue",
    response_model=AnalyticsMetric,
    summary="Net revenue",
    description="Returns total revenue minus total refunds.",
)
def net_revenue(service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_net_revenue()


@router.get(
    "/average-order-value",
    response_model=AnalyticsMetric,
    summary="Average order value",
    description="Returns the average amount across all completed orders.",
)
def average_order_value(service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_average_order_value()


@router.get(
    "/repeat-customer-revenue",
    response_model=AnalyticsMetric,
    summary="Repeat customer revenue",
    description="Returns revenue from customers who have placed more than one order.",
)
def repeat_customer_revenue(service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_repeat_customer_revenue()


@router.get(
    "/revenue-trends",
    response_model=RevenueTrendResponse,
    summary="Revenue trends",
    description="Returns revenue aggregated by day, week, or month.",
)
def revenue_trends(
    period: TrendPeriod = Query(default=TrendPeriod.daily, description="Aggregation period"),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_revenue_trends(period=period.value)


@router.get(
    "/top-customers",
    response_model=TopCustomersResponse,
    summary="Top 10 customers by spend",
    description="Returns the top 10 customers ranked by total order amount.",
)
def top_customers(
    limit: int = Query(default=10, ge=1, le=100),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return service.get_top_customers(limit=limit)