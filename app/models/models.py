"""SQLAlchemy ORM models with optimized indexing."""
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Index, Enum
)
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
import enum


class OrderStatus(str, enum.Enum):
    """Order status enumeration."""
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"


class Customer(Base):
    """Customer model."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="customer", lazy="dynamic")

    # Indexes
    __table_args__ = (
        Index("ix_customers_created_at", "created_at"),
        Index("ix_customers_email", "email"),
    )


class Order(Base):
    """Order model with composite indexes for analytics."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="completed")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    refunds = relationship("Refund", back_populates="order", lazy="dynamic")

    # Indexes - each serves a specific analytics query pattern
    __table_args__ = (
        # Single-column indexes
        Index("ix_orders_customer_id", "customer_id"),
        Index("ix_orders_status", "status"),
        Index("ix_orders_created_at", "created_at"),
        # Composite indexes for analytics
        Index("ix_orders_customer_status", "customer_id", "status"),
        Index("ix_orders_status_amount", "status", "amount"),
        Index("ix_orders_status_created", "status", "created_at"),
    )


class Refund(Base):
    """Refund model."""
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    refund_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="refunds")

    # Indexes
    __table_args__ = (
        Index("ix_refunds_order_id", "order_id"),
        Index("ix_refunds_created_at", "created_at"),
    )