"""backfill circle creators as circle_members

For every savings_circle that has no rows in circle_members, insert the
creator as an active member. This fixes circles created before the
auto-join logic was added in the create_circle endpoint.

Revision ID: 003
Revises: 002
Create Date: 2026-03-12

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Find circles that have no members yet
    orphan_circles = conn.execute(
        sa.text("""
            SELECT id, creator_id, created_at
            FROM savings_circles
            WHERE id NOT IN (
                SELECT DISTINCT circle_id FROM circle_members
            )
        """)
    ).fetchall()

    if orphan_circles:
        rows = [
            {
                "id": str(uuid.uuid4()),
                "circle_id": row.id,
                "user_id": row.creator_id,
                "joined_at": row.created_at,
                "status": "active",
            }
            for row in orphan_circles
        ]
        conn.execute(
            sa.text("""
                INSERT INTO circle_members (id, circle_id, user_id, joined_at, status)
                VALUES (:id, :circle_id, :user_id, :joined_at, :status)
            """),
            rows,
        )


def downgrade() -> None:
    # Remove members who were added by this backfill
    # (members whose joined_at matches their circle's created_at exactly)
    op.get_bind().execute(
        sa.text("""
            DELETE FROM circle_members
            WHERE (circle_id, user_id, joined_at) IN (
                SELECT cm.circle_id, cm.user_id, cm.joined_at
                FROM circle_members cm
                JOIN savings_circles sc ON sc.id = cm.circle_id
                WHERE cm.joined_at = sc.created_at
                  AND cm.user_id = sc.creator_id
            )
        """)
    )
