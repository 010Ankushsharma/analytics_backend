"""Base repository with common CRUD operations."""
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Type, TypeVar, Generic, List, Optional
from app.db.database import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic repository providing common database operations."""

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        order: str = "asc",
    ) -> List[T]:
        query = self.db.query(self.model)
        
        if sort_by and hasattr(self.model, sort_by):
            col = getattr(self.model, sort_by)
            query = query.order_by(col.desc() if order == "desc" else col.asc())
        
        return query.offset(offset).limit(limit).all()

    def count(self) -> int:
        return self.db.query(func.count(self.model.id)).scalar()

    def bulk_insert(self, records: List[dict]) -> None:
        """Batch insert using bulk_insert_mappings for performance."""
        self.db.bulk_insert_mappings(self.model, records)
        self.db.commit()

    def exists(self, id: int) -> bool:
        return self.db.query(
            self.db.query(self.model).filter(self.model.id == id).exists()
        ).scalar()