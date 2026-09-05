"""add favorites table

Revision ID: 7a9ed1cf64d9
Revises: f3a1c9d24b7e
Create Date: 2026-09-05 14:13:06.566438

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a9ed1cf64d9'
down_revision: Union[str, Sequence[str], None] = 'f3a1c9d24b7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('favorites',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('house_id', sa.Integer, nullable=True),
        sa.Column('apartment_id', sa.Integer, nullable=True),
        sa.Column('property_id', sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["house_id"], ["houses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["apartment_id"], ["apartments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["property_id"], ["property.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "house_id", name="uq_favorite_house"),
        sa.UniqueConstraint("user_id", "apartment_id", name="uq_favorite_apartment"),
        sa.UniqueConstraint("user_id", "property_id", name="uq_favorite_property"),
        sa.CheckConstraint(
            "(house_id IS NOT NULL AND apartment_id IS NULL AND property_id is NULL) OR "
            "(house_id IS NULL AND apartment_id IS NOT NULL AND property_id is NULL) OR "
            "(house_id IS NULL AND apartment_id IS NULL AND property_id IS NOT NULL)",
            name="ck_favorite_exactly_one_estate",
        ),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("favorites")
    pass
