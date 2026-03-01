"""backtest_results Sprint 8 컬럼 추가

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """backtest_results 테이블에 symbol, start_date, end_date 컬럼을 추가하고
    strategy_id를 nullable로 변경한다."""

    # strategy_id 외래키 제약 조건 삭제 후 nullable로 변경
    op.drop_constraint(
        'backtest_results_strategy_id_fkey',
        'backtest_results',
        type_='foreignkey',
    )
    op.alter_column(
        'backtest_results',
        'strategy_id',
        nullable=True,
        existing_type=sa.Integer(),
    )
    # 외래키 재생성 (nullable로 변경됨)
    op.create_foreign_key(
        'backtest_results_strategy_id_fkey',
        'backtest_results',
        'strategies',
        ['strategy_id'],
        ['id'],
    )

    # symbol 컬럼 추가
    op.add_column(
        'backtest_results',
        sa.Column('symbol', sa.String(20), nullable=True),
    )

    # start_date 컬럼 추가
    op.add_column(
        'backtest_results',
        sa.Column('start_date', sa.Date(), nullable=True),
    )

    # end_date 컬럼 추가
    op.add_column(
        'backtest_results',
        sa.Column('end_date', sa.Date(), nullable=True),
    )


def downgrade() -> None:
    """추가된 컬럼을 삭제하고 strategy_id를 다시 NOT NULL로 변경한다."""
    op.drop_column('backtest_results', 'end_date')
    op.drop_column('backtest_results', 'start_date')
    op.drop_column('backtest_results', 'symbol')

    op.drop_constraint(
        'backtest_results_strategy_id_fkey',
        'backtest_results',
        type_='foreignkey',
    )
    op.alter_column(
        'backtest_results',
        'strategy_id',
        nullable=False,
        existing_type=sa.Integer(),
    )
    op.create_foreign_key(
        'backtest_results_strategy_id_fkey',
        'backtest_results',
        'strategies',
        ['strategy_id'],
        ['id'],
    )
