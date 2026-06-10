"""Materialized view definitions and refresh operations."""
from sqlalchemy import text
from sqlalchemy.orm import Session


# SQL for creating materialized views
CREATE_MV_ORDER_SUMMARY = """
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_order_summary AS
SELECT
    COUNT(*) as total_orders,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM orders
WHERE status = 'completed';
"""

CREATE_MV_DAILY_REVENUE = """
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_revenue AS
SELECT
    DATE(orders.created_at) as date,
    SUM(orders.amount) as revenue,
    COUNT(*) as order_count
FROM orders
WHERE orders.status = 'completed'
GROUP BY DATE(orders.created_at)
ORDER BY date;
"""

CREATE_MV_CUSTOMER_SPEND = """
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_customer_spend AS
SELECT
    c.id as customer_id,
    c.name as customer_name,
    c.email as customer_email,
    SUM(o.amount) as total_spend,
    COUNT(o.id) as order_count
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.status = 'completed'
GROUP BY c.id, c.name, c.email
ORDER BY total_spend DESC;
"""

CREATE_MV_REFUND_SUMMARY = """
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_refund_summary AS
SELECT
    SUM(r.refund_amount) as total_refunds,
    COUNT(*) as refund_count
FROM refunds r;
"""

# Indexes on materialized views
CREATE_MV_INDEXES = [
    "CREATE INDEX IF NOT EXISTS ix_mv_daily_revenue_date ON mv_daily_revenue(date);",
    "CREATE INDEX IF NOT EXISTS ix_mv_customer_spend_total ON mv_customer_spend(total_spend DESC);",
]


def create_materialized_views(db: Session) -> None:
    """Create all materialized views."""
    views = [
        CREATE_MV_ORDER_SUMMARY,
        CREATE_MV_DAILY_REVENUE,
        CREATE_MV_CUSTOMER_SPEND,
        CREATE_MV_REFUND_SUMMARY,
    ]
    for view_sql in views:
        db.execute(text(view_sql))
    
    for idx_sql in CREATE_MV_INDEXES:
        db.execute(text(idx_sql))
    
    db.commit()
    print("Materialized views created successfully.")


def refresh_materialized_views(db: Session) -> None:
    """Refresh all materialized views concurrently."""
    views = [
        "mv_order_summary",
        "mv_daily_revenue",
        "mv_customer_spend",
        "mv_refund_summary",
    ]
    for view in views:
        db.execute(text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}"))
    db.commit()
    print("Materialized views refreshed.")


def drop_materialized_views(db: Session) -> None:
    """Drop all materialized views."""
    views = ["mv_order_summary", "mv_daily_revenue", "mv_customer_spend", "mv_refund_summary"]
    for view in views:
        db.execute(text(f"DROP MATERIALIZED VIEW IF EXISTS {view} CASCADE"))
    db.commit()