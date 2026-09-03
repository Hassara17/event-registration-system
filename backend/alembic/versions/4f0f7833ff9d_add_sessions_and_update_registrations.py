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
    # 2. Add registration columns
    # ---------------------------------------------------------
    #
    # These are initially nullable so that existing
    # registrations can be migrated safely.
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
    # 3. Add session_id
    # ---------------------------------------------------------
    #
    # Existing registrations may not have a session.
    # Therefore session_id is initially nullable.
    #
    # New registrations are required to provide a session
    # by the application/business logic.
    # ---------------------------------------------------------

    op.add_column(
        "registrations",
        sa.Column(
            "session_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # 4. Fill existing registration records
    # ---------------------------------------------------------
    #
    # Existing registrations already have:
    #   - user_id
    #   - registered_at
    #   - status
    #
    # Use registered_at as reserved_at.
    #
    # Since attendee_name/email did not previously exist,
    # provide safe placeholder values for existing rows.
    #
    # session_id intentionally remains NULL for old records
    # because there may not be a valid session to associate.
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
    # 5. Make required registration fields NOT NULL
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
    # 6. Create registration indexes
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
    # session_id remains nullable for legacy registrations.
    # New registrations should always have a valid session.
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
    # ---------------------------------------------------------
    # 1. Remove registration-session foreign key
    # ---------------------------------------------------------

    op.drop_constraint(
        "fk_registrations_session_id_sessions",
        "registrations",
        type_="foreignkey",
    )

    # ---------------------------------------------------------
    # 2. Remove registration indexes
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # 3. Remove session_id
    # ---------------------------------------------------------

    op.drop_column(
        "registrations",
        "session_id",
    )

    # ---------------------------------------------------------
    # 4. Remove registration columns
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # 5. Remove events index
    # ---------------------------------------------------------

    op.drop_index(
        "ix_events_organizer_id",
        table_name="events",
    )

    # ---------------------------------------------------------
    # 6. Remove sessions indexes
    # ---------------------------------------------------------

    op.drop_index(
        "ix_sessions_event_id",
        table_name="sessions",
    )

    op.drop_index(
        "ix_sessions_id",
        table_name="sessions",
    )

    # ---------------------------------------------------------
    # 7. Remove sessions table
    # ---------------------------------------------------------

    op.drop_table("sessions")