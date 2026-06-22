"""create event table"""

from alembic import op
import sqlalchemy as sa

revision = "20260622_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_event_created_at", "event", ["created_at"], unique=False)
    op.create_index("ix_event_event_type", "event", ["event_type"], unique=False)
    op.create_index("ix_event_user_id", "event", ["user_id"], unique=False)
    op.create_index(
        "idx_user_event_type", "event", ["user_id", "event_type"], unique=False
    )


def downgrade() -> None:
    op.drop_index("idx_user_event_type", table_name="event")
    op.drop_index("ix_event_user_id", table_name="event")
    op.drop_index("ix_event_event_type", table_name="event")
    op.drop_index("ix_event_created_at", table_name="event")
    op.drop_table("event")
