"""add expired_at to registrations

Revision ID: 229b04286d4a
Revises: fcde32e3ebae
Create Date: 2026-08-30

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "229b04286d4a"
down_revision: Union[str, Sequence[str], None] = "8f9537e81b63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. Add is_archived to events
    # ---------------------------------------------------------
    #
    # Existing events must remain visible by default, so
    # existing rows receive False.
    # ---------------------------------------------------------

    op.add_column(
        "events",
        sa.Column(
            "is_archived",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    # Remove the server-side default after existing rows
    # have been populated. The application/model can provide
    # the default for newly created events.
    op.alter_column(
        "events",
        "is_archived",
        server_default=None,
    )

    # ---------------------------------------------------------
    # 2. Create index for archived-event filtering
    # ---------------------------------------------------------

    op.create_index(
        "ix_events_is_archived",
        "events",
        ["is_archived"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 3. Add expired_at to registrations
    # ---------------------------------------------------------
    #
    # Existing registrations have not necessarily expired,
    # so this column must initially be nullable.
    # ---------------------------------------------------------

    op.add_column(
        "registrations",
        sa.Column(
            "expired_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # 4. Create index for expiration queries
    # ---------------------------------------------------------

    op.create_index(
        "ix_registrations_expired_at",
        "registrations",
        ["expired_at"],
        unique=False,
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # 1. Remove expired_at index
    # ---------------------------------------------------------

    op.drop_index(
        "ix_registrations_expired_at",
        table_name="registrations",
    )

    # ---------------------------------------------------------
    # 2. Remove expired_at column
    # ---------------------------------------------------------

    op.drop_column(
        "registrations",
        "expired_at",
    )

    # ---------------------------------------------------------
    # 3. Remove events is_archived index
    # ---------------------------------------------------------

    op.drop_index(
        "ix_events_is_archived",
        table_name="events",
    )

    # ---------------------------------------------------------
    # 4. Remove is_archived column
    # ---------------------------------------------------------

    op.drop_column(
        "events",
        "is_archived",
    )