"""초기 스키마 생성

Revision ID: 8a657daaed91
Revises:
Create Date: 2026-03-01 12:42:01.484474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '8a657daaed91'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """10개 테이블을 생성한다. FK 참조 관계를 고려하여 순서대로 생성한다."""

    # 1. users 테이블 - 모든 사용자 관련 테이블의 기반
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
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
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
    )

    # 2. strategies 테이블 - watchlist_items, orders, backtest_results 에서 참조
    op.create_table(
        'strategies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('strategy_type', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_preset', sa.Boolean(), nullable=False, server_default='false'),
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
        sa.PrimaryKeyConstraint('id'),
    )

    # 3. strategy_params 테이블 - strategies에 종속
    op.create_table(
        'strategy_params',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('strategy_id', sa.Integer(), nullable=False),
        sa.Column('param_key', sa.String(50), nullable=False),
        sa.Column('param_value', sa.String(200), nullable=False),
        sa.Column('param_type', sa.String(20), nullable=False),
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
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # 4. watchlist_groups 테이블 - users에 종속
    op.create_table(
        'watchlist_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
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
        sa.PrimaryKeyConstraint('id'),
    )

    # 5. watchlist_items 테이블 - watchlist_groups, strategies에 종속
    op.create_table(
        'watchlist_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('stock_code', sa.String(20), nullable=False),
        sa.Column('stock_name', sa.String(100), nullable=False),
        sa.Column('strategy_id', sa.Integer(), nullable=True),
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
        sa.ForeignKeyConstraint(['group_id'], ['watchlist_groups.id']),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # 6. orders 테이블 - users, strategies에 종속
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stock_code', sa.String(20), nullable=False),
        sa.Column('order_type', sa.String(10), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('strategy_id', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('price', sa.Numeric(12, 2), nullable=True),
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
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # 7. order_logs 테이블 - orders에 종속
    op.create_table(
        'order_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('log_type', sa.String(20), nullable=False),
        sa.Column('message', sa.String(500), nullable=False),
        sa.Column('detail', JSONB, nullable=True),
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
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # 8. portfolio_snapshots 테이블 - users에 종속
    op.create_table(
        'portfolio_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('total_value', sa.Numeric(15, 2), nullable=False),
        sa.Column('snapshot_data', JSONB, nullable=True),
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
        sa.PrimaryKeyConstraint('id'),
    )

    # 9. backtest_results 테이블 - strategies에 종속
    op.create_table(
        'backtest_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('strategy_id', sa.Integer(), nullable=False),
        sa.Column('stock_codes', JSONB, nullable=True),
        sa.Column('total_return', sa.Numeric(8, 4), nullable=True),
        sa.Column('max_drawdown', sa.Numeric(8, 4), nullable=True),
        sa.Column('sharpe_ratio', sa.Numeric(8, 4), nullable=True),
        sa.Column('win_rate', sa.Numeric(8, 4), nullable=True),
        sa.Column('result_data', JSONB, nullable=True),
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
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # 10. system_settings 테이블 - users에 선택적 종속 (전역 설정은 user_id=None)
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('setting_key', sa.String(100), nullable=False),
        sa.Column('setting_value', sa.String(500), nullable=False),
        sa.Column('setting_type', sa.String(20), nullable=False),
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
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """10개 테이블을 역순으로 삭제한다. FK 참조 관계를 고려하여 의존 테이블부터 삭제한다."""
    op.drop_table('system_settings')
    op.drop_table('backtest_results')
    op.drop_table('portfolio_snapshots')
    op.drop_table('order_logs')
    op.drop_table('orders')
    op.drop_table('watchlist_items')
    op.drop_table('watchlist_groups')
    op.drop_table('strategy_params')
    op.drop_table('strategies')
    op.drop_table('users')
