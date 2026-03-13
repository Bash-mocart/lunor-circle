"""add invite_code to savings_circles

Revision ID: 004
Revises: 003
Create Date: 2026-03-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from nanoid import generate

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _generate_code() -> str:
    return generate(_ALPHABET, 8)


def upgrade() -> None:
    op.add_column(
        "savings_circles",
        sa.Column("invite_code", sa.String(8), nullable=True),
    )
    op.create_unique_constraint(
        "uq_savings_circles_invite_code", "savings_circles", ["invite_code"]
    )
    op.create_index(
        "ix_savings_circles_invite_code", "savings_circles", ["invite_code"]
    )

    # Backfill existing rows
    conn = op.get_bind()
    rows = conn.execute(
        sa.text("SELECT id FROM savings_circles WHERE invite_code IS NULL")
    ).fetchall()

    for row in rows:
        while True:
            code = _generate_code()
            exists = conn.execute(
                sa.text("SELECT 1 FROM savings_circles WHERE invite_code = :code"),
                {"code": code},
            ).fetchone()
            if not exists:
                break
        conn.execute(
            sa.text("UPDATE savings_circles SET invite_code = :code WHERE id = :id"),
            {"code": code, "id": row.id},
        )


def downgrade() -> None:
    op.drop_index("ix_savings_circles_invite_code", table_name="savings_circles")
    op.drop_constraint(
        "uq_savings_circles_invite_code", "savings_circles", type_="unique"
    )
    op.drop_column("savings_circles", "invite_code")
