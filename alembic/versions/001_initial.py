"""Initial schema creation.

Revision ID: 001
Create Date: 2026-06-09
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Customers table
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_customers_created_at', 'customers', ['created_at'])
    op.create_index('ix_customers_email', 'customers', ['email'])

    # Orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_orders_customer_id', 'orders', ['customer_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    op.create_index('ix_orders_created_at', 'orders', ['created_at'])
    op.create_index('ix_orders_customer_status', 'orders', ['customer_id', 'status'])
    op.create_index('ix_orders_status_amount', 'orders', ['status', 'amount'])
    op.create_index('ix_orders_status_created', 'orders', ['status', 'created_at'])

    # Refunds table
    op.create_table(
        'refunds',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('refund_amount', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_refunds_order_id', 'refunds', ['order_id'])
    op.create_index('ix_refunds_created_at', 'refunds', ['created_at'])


def downgrade():
    op.drop_table('refunds')
    op.drop_table('orders')
    op.drop_table('customers')