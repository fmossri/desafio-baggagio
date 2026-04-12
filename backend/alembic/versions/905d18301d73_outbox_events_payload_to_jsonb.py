"""outbox_events payload to jsonb

Revision ID: 905d18301d73
Revises: 89838e7b5947
Create Date: 2026-04-12 11:20:29.910830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '905d18301d73'
down_revision: Union[str, Sequence[str], None] = '89838e7b5947'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "outbox_events",
        "payload",
        existing_type=sa.JSON(),
        type_=JSONB(),
        postgresql_using="payload::jsonb",
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "outbox_events",
        "payload",
        existing_type=JSONB(),
        type_=sa.JSON(),
        postgresql_using="payload::json",
        existing_nullable=False,
    )
