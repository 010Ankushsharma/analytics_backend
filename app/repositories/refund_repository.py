"""Refund-specific repository operations."""
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.repositories.base_repository import BaseRepository
from app.models.models import Refund


class RefundRepository(BaseRepository[Refund]):
    """Repository for Refund data access."""

    def __init__(self, db: Session):
        super().__init__(Refund, db)

    def get_total_refunds(self) -> float:
        """Sum of all refund amounts."""
        result = self.db.query(func.sum(Refund.refund_amount)).scalar()
        return float(result or 0)

    def get_total_refund_count(self) -> int:
        """Count of all refunds."""
        return self.db.query(func.count(Refund.id)).scalar() or 0

    def get_max_id(self) -> int:
        result = self.db.query(func.max(Refund.id)).scalar()
        return result or 0