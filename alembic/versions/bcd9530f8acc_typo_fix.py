"""typo fix

Revision ID: bcd9530f8acc
Revises: 0b845eee7c50
Create Date: 2026-09-22 10:27:04.574937

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bcd9530f8acc'
down_revision: Union[str, Sequence[str], None] = '0b845eee7c50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
