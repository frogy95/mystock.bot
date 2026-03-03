"""Sprint 15 사용자별 전략/백테스트 데이터 격리

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-03-03 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """strategies.user_id 및 backtest_results.user_id 컬럼 추가."""

    # 1. strategies 테이블에 user_id 컬럼 추가 (nullable — 프리셋은 NULL)
    op.add_column(
        'strategies',
        sa.Column('user_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        'fk_strategies_user_id',
        'strategies', 'users',
        ['user_id'], ['id'],
    )

    # 2. backtest_results 테이블에 user_id 컬럼 추가
    #    기존 레코드가 있을 수 있으므로 먼저 nullable로 추가 후 admin 할당 → NOT NULL로 변경
    op.add_column(
        'backtest_results',
        sa.Column('user_id', sa.Integer(), nullable=True),
    )

    # 기존 backtest_results 레코드를 admin 사용자(id=1)에 할당
    op.execute(
        "UPDATE backtest_results SET user_id = (SELECT id FROM users ORDER BY id LIMIT 1) "
        "WHERE user_id IS NULL"
    )

    # NOT NULL 제약 적용
    op.alter_column('backtest_results', 'user_id', nullable=False)

    op.create_foreign_key(
        'fk_backtest_results_user_id',
        'backtest_results', 'users',
        ['user_id'], ['id'],
    )


def downgrade() -> None:
    """변경 사항을 롤백한다."""
    op.drop_constraint('fk_backtest_results_user_id', 'backtest_results', type_='foreignkey')
    op.drop_column('backtest_results', 'user_id')

    op.drop_constraint('fk_strategies_user_id', 'strategies', type_='foreignkey')
    op.drop_column('strategies', 'user_id')
