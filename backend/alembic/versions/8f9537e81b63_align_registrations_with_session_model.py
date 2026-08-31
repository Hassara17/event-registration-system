"""align registrations with session model

Revision ID: 8f9537e81b63
Revises: 4f0f7833ff9d
Create Date: 2026-08-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "8f9537e81b63"

down_revision: Union[str, Sequence[str], None] = "4f0f7833ff9d"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove the old event_id foreign key
    op.drop_constraint(
        "registrations_event_id_fkey",
        "registrations",
        type_="foreignkey",
    )

    # Remove legacy registered_at column
    op.drop_column(
        "registrations",
        "registered_at",
    )

    # Remove legacy event_id column
    op.drop_column(
        "registrations",
        "event_id",
    )

    # session_id is required by the current Registration model
    op.alter_column(
        "registrations",
        "session_id",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    # Make session_id nullable again
    op.alter_column(
        "registrations",
        "session_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    # Restore event_id
    op.add_column(
        "registrations",
        sa.Column(
            "event_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # Restore registered_at
    op.add_column(
        "registrations",
        sa.Column(
            "registered_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    # Restore event foreign key
    op.create_foreign_key(
        "registrations_event_id_fkey",
        "registrations",
        "events",
        ["event_id"],
        ["id"],
    )