"""holdings 테이블 추가

Revision ID: a1b2c3d4e5f6
Revises: 8a657daaed91
Create Date: 2026-03-01 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '8a657daaed91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """holdings 테이블을 생성한다."""
    op.create_table(
        'holdings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stock_code', sa.String(20), nullable=False),
        sa.Column('stock_name', sa.String(100), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_price', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('current_price', sa.Numeric(12, 2), nullable=True),
        sa.Column('stop_loss_rate', sa.Numeric(6, 2), nullable=True),
        sa.Column('take_profit_rate', sa.Numeric(6, 2), nullable=True),
        sa.Column('sell_strategy_id', sa.Integer(), nullable=True),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['sell_strategy_id'], ['strategies.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """holdings 테이블을 삭제한다."""
    op.drop_table('holdings')
