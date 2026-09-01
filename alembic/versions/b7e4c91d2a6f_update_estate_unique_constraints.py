"""update estate unique constraints

Revision ID: b7e4c91d2a6f
Revises: 926498f0582e
Create Date: 2026-09-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b7e4c91d2a6f'
down_revision: Union[str, Sequence[str], None] = '926498f0582e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("uq_houses_url_title", "houses", type_="unique")
    op.create_unique_constraint(
        "uq_houses_title_price_city_living_space",
        "houses",
        ["title", "price", "city", "living_space"],
    )

    op.drop_constraint("uq_apartments_url_title", "apartments", type_="unique")
    op.create_unique_constraint(
        "uq_apartments_title_price_city_living_space",
        "apartments",
        ["title", "price", "city", "living_space"],
    )

    op.drop_constraint("uq_property_url_title", "property", type_="unique")
    op.create_unique_constraint(
        "uq_property_title_price_city_space",
        "property",
        ["title", "price", "city", "space"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_property_title_price_city_space", "property", type_="unique")
    op.create_unique_constraint(
        "uq_property_url_title",
        "property",
        ["url", "title"],
    )

    op.drop_constraint("uq_apartments_title_price_city_living_space", "apartments", type_="unique")
    op.create_unique_constraint(
        "uq_apartments_url_title",
        "apartments",
        ["url", "title"],
    )

    op.drop_constraint("uq_houses_title_price_city_living_space", "houses", type_="unique")
    op.create_unique_constraint(
        "uq_houses_url_title",
        "houses",
        ["url", "title"],
    )
