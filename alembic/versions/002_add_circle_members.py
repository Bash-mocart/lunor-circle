"""add circle_members table

Revision ID: 002
Revises: 001
Create Date: 2026-03-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "circle_members",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column(
            "circle_id",
            sa.String(36),
            sa.ForeignKey("savings_circles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
    )
    op.create_index("ix_circle_members_circle_id", "circle_members", ["circle_id"])
    op.create_index("ix_circle_members_user_id", "circle_members", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_circle_members_user_id", table_name="circle_members")
    op.drop_index("ix_circle_members_circle_id", table_name="circle_members")
    op.drop_table("circle_members")
