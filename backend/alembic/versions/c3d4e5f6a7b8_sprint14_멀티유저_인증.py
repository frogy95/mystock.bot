"""Sprint 14 멀티유저 인증 - User 모델 확장 및 InvitationCode 테이블 추가

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """User 테이블 컬럼 추가 및 InvitationCode 테이블 생성."""

    # 1. users 테이블에 새 컬럼 추가
    op.add_column('users', sa.Column('email', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('password_hash', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('role', sa.String(20), nullable=False, server_default='user'))
    op.add_column('users', sa.Column('invited_by', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='false'))

    # 2. users.email 고유 인덱스
    op.create_unique_constraint('uq_users_email', 'users', ['email'])

    # 3. users.invited_by FK 추가
    op.create_foreign_key(
        'fk_users_invited_by',
        'users', 'users',
        ['invited_by'], ['id'],
    )

    # 4. invitation_codes 테이블 생성
    op.create_table(
        'invitation_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(64), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('used_by', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code', name='uq_invitation_codes_code'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_invitation_codes_created_by'),
        sa.ForeignKeyConstraint(['used_by'], ['users.id'], name='fk_invitation_codes_used_by'),
    )

    # 5. 기존 관리자 계정의 is_approved를 true로 설정 (기존 사용자 마이그레이션)
    op.execute("UPDATE users SET is_approved = true, role = 'admin'")


def downgrade() -> None:
    """변경 사항을 롤백한다."""
    op.drop_table('invitation_codes')
    op.drop_constraint('fk_users_invited_by', 'users', type_='foreignkey')
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    op.drop_column('users', 'is_approved')
    op.drop_column('users', 'invited_by')
    op.drop_column('users', 'role')
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'email')
