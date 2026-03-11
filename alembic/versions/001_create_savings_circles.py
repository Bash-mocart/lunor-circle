"""create savings_circles table

Revision ID: 001
Revises:
Create Date: 2026-03-11

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "savings_circles",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column("creator_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("members", sa.Integer(), nullable=False),
        sa.Column("frequency", sa.String(20), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("payout_count", sa.Integer(), nullable=False),
        sa.Column("penalty_percent", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("grace_period_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("start_when_members", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_savings_circles_creator_id", "savings_circles", ["creator_id"])


def downgrade() -> None:
    op.drop_index("ix_savings_circles_creator_id", table_name="savings_circles")
    op.drop_table("savings_circles")
