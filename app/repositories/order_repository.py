"""Order-specific repository operations."""
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.repositories.base_repository import BaseRepository
from app.models.models import Order
from typing import List, Dict


class OrderRepository(BaseRepository[Order]):
    """Repository for Order data access."""

    def __init__(self, db: Session):
        super().__init__(Order, db)

    def get_total_revenue(self) -> float:
        """Sum of all completed order amounts."""
        result = self.db.query(func.sum(Order.amount)).filter(
            Order.status == "completed"
        ).scalar()
        return float(result or 0)

    def get_average_order_value(self) -> float:
        """Average amount of completed orders."""
        result = self.db.query(func.avg(Order.amount)).filter(
            Order.status == "completed"
        ).scalar()
        return float(result or 0)

    def get_repeat_customer_revenue(self) -> float:
        """Revenue from customers with more than 1 order."""
        sql = text("""
            SELECT COALESCE(SUM(o.amount), 0) as revenue
            FROM orders o
            WHERE o.status = 'completed'
            AND o.customer_id IN (
                SELECT customer_id 
                FROM orders 
                WHERE status = 'completed'
                GROUP BY customer_id 
                HAVING COUNT(*) > 1
            )
        """)
        result = self.db.execute(sql).scalar()
        return float(result or 0)

    def get_revenue_trends_daily(self) -> List[Dict]:
        """Daily revenue aggregation from materialized view."""
        sql = text("SELECT date, revenue, order_count FROM mv_daily_revenue ORDER BY date")
        rows = self.db.execute(sql).fetchall()
        return [{"period": str(r[0]), "revenue": float(r[1]), "order_count": int(r[2])} for r in rows]

    def get_revenue_trends_weekly(self) -> List[Dict]:
        """Weekly revenue aggregation."""
        sql = text("""
            SELECT DATE_TRUNC('week', date) as week, 
                   SUM(revenue) as revenue, 
                   SUM(order_count) as order_count
            FROM mv_daily_revenue
            GROUP BY week
            ORDER BY week
        """)
        rows = self.db.execute(sql).fetchall()
        return [{"period": str(r[0].date()), "revenue": float(r[1]), "order_count": int(r[2])} for r in rows]

    def get_revenue_trends_monthly(self) -> List[Dict]:
        """Monthly revenue aggregation."""
        sql = text("""
            SELECT DATE_TRUNC('month', date) as month, 
                   SUM(revenue) as revenue, 
                   SUM(order_count) as order_count
            FROM mv_daily_revenue
            GROUP BY month
            ORDER BY month
        """)
        rows = self.db.execute(sql).fetchall()
        return [{"period": str(r[0].date()), "revenue": float(r[1]), "order_count": int(r[2])} for r in rows]

    def get_top_customers(self, limit: int = 10) -> List[Dict]:
        """Top customers by spend from materialized view."""
        sql = text(f"""
            SELECT customer_id, customer_name, customer_email, total_spend, order_count
            FROM mv_customer_spend
            LIMIT {limit}
        """)
        rows = self.db.execute(sql).fetchall()
        return [
            {
                "customer_id": r[0],
                "name": r[1],
                "email": r[2],
                "total_spend": float(r[3]),
                "order_count": int(r[4]),
            }
            for r in rows
        ]

    def get_max_id(self) -> int:
        result = self.db.query(func.max(Order.id)).scalar()
        return result or 0