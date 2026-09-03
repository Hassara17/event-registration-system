"""add session staff assignments

Revision ID: c77d310065c1
Revises: 229b04286d4a
Create Date: 2026-08-30 20:37:14.497190

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c77d310065c1"
down_revision: Union[str, Sequence[str], None] = "229b04286d4a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "session_staff",
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("staff_id", sa.Integer(), nullable=False),

        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["staff_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "session_id",
            "staff_id",
        ),
    )


def downgrade() -> None:
    op.drop_table("session_staff")