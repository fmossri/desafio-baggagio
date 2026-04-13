"""add product_audit_log table

Revision ID: 77e9aa10baa4
Revises: 80252c49f316
Create Date: 2026-04-13 17:08:34.485803

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '77e9aa10baa4'
down_revision: Union[str, Sequence[str], None] = '80252c49f316'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_audit_log",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("event_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("actor_user_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("payload", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_audit_log_event_id", "product_audit_log", ["event_id"], unique=False)
    op.create_index("ix_product_audit_log_actor_user_id", "product_audit_log", ["actor_user_id"], unique=False)
    op.create_index("ix_product_audit_log_product_id", "product_audit_log", ["product_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_product_audit_log_product_id", "product_audit_log")
    op.drop_index("ix_product_audit_log_actor_user_id", "product_audit_log")
    op.drop_index("ix_product_audit_log_event_id", "product_audit_log")
    op.drop_table("product_audit_log")
