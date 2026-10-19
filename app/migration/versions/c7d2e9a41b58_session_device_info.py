"""Session device info

Revision ID: c7d2e9a41b58
Revises: a3b5f0e3e6cd
Create Date: 2026-10-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7d2e9a41b58'
down_revision: Union[str, None] = 'a3b5f0e3e6cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user_sessions', sa.Column('device_name', sa.String(length=128), nullable=True))
    op.add_column('user_sessions', sa.Column('platform', sa.String(length=16), nullable=True))
    op.add_column('user_sessions', sa.Column('os_version', sa.String(length=32), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user_sessions', 'os_version')
    op.drop_column('user_sessions', 'platform')
    op.drop_column('user_sessions', 'device_name')
