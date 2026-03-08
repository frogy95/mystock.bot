"""sprint23 커스텀 전략 조건 컬럼 추가

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-03-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # strategies 테이블에 커스텀 전략 조건 컬럼 추가
    op.add_column('strategies', sa.Column('buy_conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('strategies', sa.Column('sell_conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('strategies', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('strategies', 'description')
    op.drop_column('strategies', 'sell_conditions')
    op.drop_column('strategies', 'buy_conditions')
