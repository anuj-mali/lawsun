"""add timestamps to parent_chunks

Revision ID: 094b5fd57bef
Revises: 6091c50a1f22
Create Date: 2026-05-01 12:36:31.463530

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "094b5fd57bef"  # pragma: allowlist secret
down_revision: Union[str, Sequence[str], None] = (
    "6091c50a1f22"  # pragma: allowlist secret
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "parent_chunks",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "parent_chunks",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("parent_chunks", "updated_at")
    op.drop_column("parent_chunks", "created_at")
