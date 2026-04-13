"""add pg_trgm index on products name

Revision ID: 80252c49f316
Revises: 905d18301d73
Create Date: 2026-04-13 05:19:25.906703

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80252c49f316'
down_revision: Union[str, Sequence[str], None] = '905d18301d73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_products_name_trgm
        ON products
        USING gin (name gin_trgm_ops)
        """
    )


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS ix_products_name_trgm')
