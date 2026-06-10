"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


# ---- Request Schemas ----

class PaginationParams(BaseModel):
    """Pagination query parameters."""
    limit: int = Field(default=100, ge=1, le=10000)
    offset: int = Field(default=0, ge=0)
    sort_by: Optional[str] = None
    order: Optional[str] = Field(default="asc", pattern="^(asc|desc)$")


class TrendPeriod(str, Enum):
    """Revenue trend aggregation periods."""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


# ---- Response Schemas ----

class CustomerResponse(BaseModel):
    """Customer API response."""
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Order API response."""
    id: int
    customer_id: int
    amount: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RefundResponse(BaseModel):
    """Refund API response."""
    id: int
    order_id: int
    refund_amount: float
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    data: List[dict]
    total: int
    limit: int
    offset: int
    has_more: bool


class AnalyticsMetric(BaseModel):
    """Single analytics metric response."""
    metric: str
    value: float
    cached: bool = False
    computed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "metric": "total_revenue",
                "value": 49987234.56,
                "cached": True,
                "computed_at": "2026-06-09T10:30:00Z"
            }
        }


class RevenueTrendItem(BaseModel):
    """Single data point in revenue trend."""
    period: str
    revenue: float
    order_count: int


class RevenueTrendResponse(BaseModel):
    """Revenue trend response."""
    metric: str = "revenue_trends"
    period_type: str
    data: List[RevenueTrendItem]
    cached: bool = False
    computed_at: datetime = Field(default_factory=datetime.utcnow)


class TopCustomerItem(BaseModel):
    """Top customer entry."""
    customer_id: int
    name: str
    email: str
    total_spend: float
    order_count: int


class TopCustomersResponse(BaseModel):
    """Top customers response."""
    metric: str = "top_customers"
    data: List[TopCustomerItem]
    cached: bool = False
    computed_at: datetime = Field(default_factory=datetime.utcnow)


class IngestionStatus(BaseModel):
    """Ingestion progress status."""
    entity: str
    total_records: int
    ingested_records: int
    progress_percent: float
    status: str