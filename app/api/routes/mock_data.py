"""Mock data API endpoints serving CSV data with pagination."""
from fastapi import APIRouter, Query, HTTPException
from app.schemas.schemas import PaginatedResponse
from app.core.config import get_settings
import pandas as pd
import os
from functools import lru_cache
from typing import Optional

router = APIRouter(tags=["Mock Data APIs"])
settings = get_settings()


@lru_cache(maxsize=3)
def _load_csv(entity: str) -> pd.DataFrame:
    """Load and cache CSV data in memory for efficient serving."""
    filepath = os.path.join(settings.data_dir, f"{entity}.csv")
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail=f"Data file not found: {filepath}. Run generate_data.py first."
        )
    return pd.read_csv(filepath)


def _paginate(
    entity: str,
    limit: int,
    offset: int,
    sort_by: Optional[str],
    order: str,
) -> PaginatedResponse:
    """Generic pagination handler."""
    df = _load_csv(entity)
    total = len(df)

    if sort_by and sort_by in df.columns:
        ascending = order == "asc"
        df = df.sort_values(by=sort_by, ascending=ascending)

    page = df.iloc[offset: offset + limit]
    data = page.to_dict(orient="records")

    return PaginatedResponse(
        data=data,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total,
    )


@router.get(
    "/customers",
    response_model=PaginatedResponse,
    summary="Get paginated customers",
    description="Returns customer records with pagination, sorting support.",
)
def get_customers(
    limit: int = Query(default=100, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
    sort_by: Optional[str] = Query(default=None, description="Column to sort by"),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
):
    """Fetch paginated customer records from generated CSV data."""
    return _paginate("customers", limit, offset, sort_by, order)


@router.get(
    "/orders",
    response_model=PaginatedResponse,
    summary="Get paginated orders",
    description="Returns order records with pagination, sorting support.",
)
def get_orders(
    limit: int = Query(default=100, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
    sort_by: Optional[str] = Query(default=None),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
):
    """Fetch paginated order records from generated CSV data."""
    return _paginate("orders", limit, offset, sort_by, order)


@router.get(
    "/refunds",
    response_model=PaginatedResponse,
    summary="Get paginated refunds",
    description="Returns refund records with pagination, sorting support.",
)
def get_refunds(
    limit: int = Query(default=100, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
    sort_by: Optional[str] = Query(default=None),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
):
    """Fetch paginated refund records from generated CSV data."""
    return _paginate("refunds", limit, offset, sort_by, order)