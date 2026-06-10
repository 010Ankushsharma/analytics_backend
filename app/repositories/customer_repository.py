"""Customer-specific repository operations."""
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.models import Customer


class CustomerRepository(BaseRepository[Customer]):
    """Repository for Customer data access."""

    def __init__(self, db: Session):
        super().__init__(Customer, db)

    def get_max_id(self) -> int:
        """Get the maximum customer ID (for deduplication)."""
        from sqlalchemy import func
        result = self.db.query(func.max(Customer.id)).scalar()
        return result or 0