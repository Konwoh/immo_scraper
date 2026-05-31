"""Allow properties in search_results check constraint

Revision ID: c8f4a9d2e7b1
Revises: 9173ded3413b
Create Date: 2026-05-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c8f4a9d2e7b1"
down_revision: Union[str, Sequence[str], None] = "9173ded3413b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CONSTRAINT_NAME = "ck_search_result_exactly_one_estate"
TABLE_NAME = "search_results"


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(CONSTRAINT_NAME, TABLE_NAME, type_="check")
    op.create_check_constraint(
        CONSTRAINT_NAME,
        TABLE_NAME,
        "(house_id IS NOT NULL AND apartment_id IS NULL AND property_id IS NULL) OR "
        "(house_id IS NULL AND apartment_id IS NOT NULL AND property_id IS NULL) OR "
        "(house_id IS NULL AND apartment_id IS NULL AND property_id IS NOT NULL)",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(CONSTRAINT_NAME, TABLE_NAME, type_="check")
    op.create_check_constraint(
        CONSTRAINT_NAME,
        TABLE_NAME,
        "(house_id IS NOT NULL AND apartment_id IS NULL AND property_id IS NULL) OR "
        "(house_id IS NULL AND apartment_id IS NOT NULL AND property_id IS NULL)",
    )
