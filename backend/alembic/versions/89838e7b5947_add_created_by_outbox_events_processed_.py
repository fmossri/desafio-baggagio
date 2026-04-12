"""add created_by outbox_events processed_events

Revision ID: 89838e7b5947
Revises: f4265c33497e
Create Date: 2026-04-12 03:02:50.183611

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89838e7b5947'
down_revision: Union[str, Sequence[str], None] = 'f4265c33497e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('products', sa.Column('created_by', sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_products_created_by_users",
        "products",
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "outbox_events",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("aggregate_type", sa.String(length=64), nullable=False),
        sa.Column("aggregate_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
    )
    op.create_index("ix_outbox_events_unpublished", "outbox_events", ["published_at"], unique=False)

    op.create_table(
        "processed_events",
        sa.Column("event_id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

def downgrade() -> None:
    op.drop_table("processed_events")
    op.drop_index("ix_outbox_events_unpublished", table_name="outbox_events")
    op.drop_table("outbox_events")
    op.drop_constraint("fk_products_created_by_users", "products", type_="foreignkey")
    op.drop_column("products", "created_by")