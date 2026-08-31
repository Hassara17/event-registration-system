"""add sessions and update registrations

Revision ID: 4f0f7833ff9d
Revises: 2d555afb76de
Create Date: 2026-08-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4f0f7833ff9d"
down_revision: Union[str, Sequence[str], None] = "2d555afb76de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. Create sessions table
    # ---------------------------------------------------------

    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),

        sa.CheckConstraint(
            "duration > 0",
            name="check_session_duration_positive",
        ),

        sa.CheckConstraint(
            "capacity > 0",
            name="check_session_capacity_positive",
        ),

        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_sessions_id",
        "sessions",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_sessions_event_id",
        "sessions",
        ["event_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 2. Add new registration columns as NULLABLE first
    # ---------------------------------------------------------

    op.add_column(
        "registrations",
        sa.Column(
            "attendee_name",
            sa.String(length=200),
            nullable=True,
        ),
    )

    op.add_column(
        "registrations",
        sa.Column(
            "attendee_email",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "registrations",
        sa.Column(
            "reserved_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.add_column(
        "registrations",
        sa.Column(
            "confirmed_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.add_column(
        "registrations",
        sa.Column(
            "checked_in_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.add_column(
        "registrations",
        sa.Column(
            "cancelled_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # 3. Fill existing records
    # ---------------------------------------------------------
    #
    # Existing registrations already have:
    #   user_id
    #   registered_at
    #   status
    #
    # We use registered_at as reserved_at.
    #
    # attendee_name/email are temporarily populated with
    # safe placeholder values.
    #
    # This allows the migration to succeed.
    # ---------------------------------------------------------

    op.execute(
        """
        UPDATE registrations
        SET
            attendee_name = 'Existing Attendee',
            attendee_email = 'existing_' || id || '@example.com',
            reserved_at = registered_at
        WHERE attendee_name IS NULL
           OR attendee_email IS NULL
           OR reserved_at IS NULL
        """
    )

    # ---------------------------------------------------------
    # 4. Set columns to NOT NULL after existing rows are fixed
    # ---------------------------------------------------------

    op.alter_column(
        "registrations",
        "attendee_name",
        existing_type=sa.String(length=200),
        nullable=False,
    )

    op.alter_column(
        "registrations",
        "attendee_email",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    op.alter_column(
        "registrations",
        "reserved_at",
        existing_type=sa.DateTime(),
        nullable=False,
    )

    # ---------------------------------------------------------
    # 5. session_id becomes required
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    # Existing registrations currently have session_id NULL.
    #
    # We cannot safely make session_id NOT NULL until every
    # existing registration has a valid session.
    #
    # Therefore, leave it nullable for this migration.
    #
    # New registrations can still require session_id at the
    # application level.
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # 6. Create indexes
    # ---------------------------------------------------------

    op.create_index(
        "ix_registrations_attendee_email",
        "registrations",
        ["attendee_email"],
        unique=False,
    )

    op.create_index(
        "ix_registrations_reserved_at",
        "registrations",
        ["reserved_at"],
        unique=False,
    )

    op.create_index(
        "ix_registrations_session_id",
        "registrations",
        ["session_id"],
        unique=False,
    )

    op.create_index(
        "ix_registrations_status",
        "registrations",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_registrations_user_id",
        "registrations",
        ["user_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 7. Add session foreign key
    # ---------------------------------------------------------
    #
    # Existing event_id is kept for now so we don't lose data.
    #
    # Once existing registrations are migrated to sessions,
    # event_id can be removed in a later migration.
    # ---------------------------------------------------------

    op.create_foreign_key(
        "fk_registrations_session_id_sessions",
        "registrations",
        "sessions",
        ["session_id"],
        ["id"],
    )

    # ---------------------------------------------------------
    # 8. Events organizer index
    # ---------------------------------------------------------

    op.create_index(
        "ix_events_organizer_id",
        "events",
        ["organizer_id"],
        unique=False,
    )


def downgrade() -> None:
    # Remove foreign key
    op.drop_constraint(
        "fk_registrations_session_id_sessions",
        "registrations",
        type_="foreignkey",
    )

    # Remove indexes
    op.drop_index(
        "ix_registrations_user_id",
        table_name="registrations",
    )

    op.drop_index(
        "ix_registrations_status",
        table_name="registrations",
    )

    op.drop_index(
        "ix_registrations_session_id",
        table_name="registrations",
    )

    op.drop_index(
        "ix_registrations_reserved_at",
        table_name="registrations",
    )

    op.drop_index(
        "ix_registrations_attendee_email",
        table_name="registrations",
    )

    # Remove new registration columns
    op.drop_column(
        "registrations",
        "cancelled_at",
    )

    op.drop_column(
        "registrations",
        "checked_in_at",
    )

    op.drop_column(
        "registrations",
        "confirmed_at",
    )

    op.drop_column(
        "registrations",
        "reserved_at",
    )

    op.drop_column(
        "registrations",
        "attendee_email",
    )

    op.drop_column(
        "registrations",
        "attendee_name",
    )

    # Remove events index
    op.drop_index(
        "ix_events_organizer_id",
        table_name="events",
    )

    # Remove sessions indexes/table
    op.drop_index(
        "ix_sessions_event_id",
        table_name="sessions",
    )

    op.drop_index(
        "ix_sessions_id",
        table_name="sessions",
    )

    op.drop_table("sessions")