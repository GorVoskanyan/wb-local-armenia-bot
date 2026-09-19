"""initial migration

Revision ID: 0001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('role', sa.Enum('buyer', 'seller', name='userrole'), nullable=False),
        sa.Column('language_preference', sa.String(length=5), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'sellers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('wb_api_key_encrypted', sa.String(length=1000), nullable=False),
        sa.Column('shop_name', sa.String(length=255), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('wb_sku_id', sa.BigInteger(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('discount_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('category', sa.String(length=255), nullable=False),
        sa.Column('stock_quantity', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(length=1000), nullable=True),
        sa.Column('is_local_stock', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['seller_id'], ['sellers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_wb_sku_id'), 'products', ['wb_sku_id'], unique=True)
    op.create_index(op.f('ix_products_category'), 'products', ['category'], unique=False)
    op.create_index(op.f('ix_products_is_local_stock'), 'products', ['is_local_stock'], unique=False)
    op.create_index('idx_category_local', 'products', ['category', 'is_local_stock'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_category_local', table_name='products')
    op.drop_index(op.f('ix_products_is_local_stock'), table_name='products')
    op.drop_index(op.f('ix_products_category'), table_name='products')
    op.drop_index(op.f('ix_products_wb_sku_id'), table_name='products')
    op.drop_table('products')
    op.drop_table('sellers')
    op.drop_table('users')
