"""remove unique constraint from long_url

Revision ID: 2ee792f0ae3b
Revises: 33b713a717d4
Create Date: 2026-05-07 19:01:16.994736

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ee792f0ae3b'
down_revision: Union[str, Sequence[str], None] = '33b713a717d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f('ix_url_map_long_url'), table_name='url_map')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_index(op.f('ix_url_map_long_url'), 'url_map', ['long_url'], unique=True)
