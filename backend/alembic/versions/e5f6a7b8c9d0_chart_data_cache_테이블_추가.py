"""chart_data_cache 테이블 추가

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-03-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'chart_data_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('trade_date', sa.Date(), nullable=False),
        sa.Column('open', sa.Numeric(12, 2), nullable=False),
        sa.Column('high', sa.Numeric(12, 2), nullable=False),
        sa.Column('low', sa.Numeric(12, 2), nullable=False),
        sa.Column('close', sa.Numeric(12, 2), nullable=False),
        sa.Column('volume', sa.BigInteger(), nullable=False),
        sa.Column('source', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol', 'trade_date', name='uq_chart_symbol_date'),
    )
    op.create_index('ix_chart_data_cache_symbol', 'chart_data_cache', ['symbol'])


def downgrade() -> None:
    op.drop_index('ix_chart_data_cache_symbol', table_name='chart_data_cache')
    op.drop_table('chart_data_cache')
