"""Initial revision

Revision ID: a3b5f0e3e6cd
Revises:
Create Date: 2026-09-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3b5f0e3e6cd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('users',
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('login', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('role', sa.Enum('admin', 'user', name='user_role'), nullable=False),
    sa.Column('avatar', sa.Text(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('item_id'),
    sa.UniqueConstraint('login')
    )
    op.create_table('keys',
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('public_key', sa.Text(), nullable=False),
    sa.Column('encrypted_private_key', sa.Text(), nullable=False),
    sa.Column('version', sa.Numeric(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.item_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('item_id')
    )
    op.create_table('folders',
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('parent_id', sa.String(), nullable=True),
    sa.Column('key_id', sa.Text(), nullable=False),
    sa.Column('payload', sa.Text(), nullable=False),
    sa.Column('order_index', sa.Float(), nullable=False, server_default='0'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.item_id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['folders.item_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('item_id')
    )
    op.create_table('notes',
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('folder_id', sa.String(), nullable=True),
    sa.Column('key_id', sa.Text(), nullable=False),
    sa.Column('payload', sa.Text(), nullable=False),
    sa.Column('order_index', sa.Float(), nullable=False, server_default='0'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.item_id'], ),
    sa.ForeignKeyConstraint(['folder_id'], ['folders.item_id'], name='fk_notes_folder_id_folders'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('item_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('notes')
    op.drop_table('folders')
    op.drop_table('keys')
    op.drop_table('users')
    sa.Enum(name='user_role').drop(op.get_bind(), checkfirst=True)
