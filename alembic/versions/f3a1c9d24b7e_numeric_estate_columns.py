"""convert price, living_space, rent_extra_costs, space to double precision

Revision ID: f3a1c9d24b7e
Revises: 01f1054a972f
Create Date: 2026-09-03 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f3a1c9d24b7e'
down_revision: Union[str, Sequence[str], None] = '01f1054a972f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Regel A – Preis-Format ("499.000 €" mit Tausenderpunkt, oder roher Maschinenwert)
def _price_expr(col: str) -> str:
    return f"""
        CASE
            WHEN {col} ~ '€'
                THEN NULLIF(regexp_replace(replace(replace({col}, '.', ''), ',', '.'), '[^0-9.]', '', 'g'), '')::double precision
            WHEN {col} ~ '^[0-9]+([.,][0-9]+)?$'
                THEN replace({col}, ',', '.')::double precision
            ELSE NULL
        END
    """


# Regel B – Flächen-Format (Komma = Dezimal + Tausenderpunkt; sonst Punkt = Dezimal,
# ausser die Zahl besteht nur aus .NNN-Tausendergruppen wie "1.140")
def _area_expr(col: str) -> str:
    return f"""
        CASE
            WHEN {col} !~ '[0-9]' THEN NULL
            WHEN {col} ~ ','
                THEN NULLIF(regexp_replace(replace(replace({col}, '.', ''), ',', '.'), '[^0-9.]', '', 'g'), '')::double precision
            WHEN regexp_replace({col}, '[^0-9.]', '', 'g') ~ '^[0-9]{{1,3}}(\\.[0-9]{{3}})+$'
                THEN replace(regexp_replace({col}, '[^0-9.]', '', 'g'), '.', '')::double precision
            ELSE NULLIF(regexp_replace({col}, '[^0-9.]', '', 'g'), '')::double precision
        END
    """


def _alter(col: str, expr: str) -> str:
    return f"ALTER COLUMN {col} TYPE double precision USING ({expr})"


def _alter_back(col: str) -> str:
    return f"ALTER COLUMN {col} TYPE varchar USING {col}::text"


def upgrade() -> None:
    for table in ("houses", "apartments"):
        op.drop_constraint(f"uq_{table}_title_price_city_living_space", table, type_="unique")
        op.execute(
            f"ALTER TABLE {table} "
            + _alter("price", _price_expr("price")) + ", "
            + _alter("rent_extra_costs", _price_expr("rent_extra_costs")) + ", "
            + _alter("living_space", _area_expr("living_space"))
        )
        op.create_unique_constraint(
            f"uq_{table}_title_price_city_living_space",
            table,
            ["title", "price", "city", "living_space"],
        )

    op.drop_constraint("uq_property_title_price_city_space", "property", type_="unique")
    op.execute(
        "ALTER TABLE property "
        + _alter("price", _price_expr("price")) + ", "
        + _alter("space", _area_expr("space"))
    )
    op.create_unique_constraint(
        "uq_property_title_price_city_space",
        "property",
        ["title", "price", "city", "space"],
    )


def downgrade() -> None:
    for table in ("houses", "apartments"):
        op.drop_constraint(f"uq_{table}_title_price_city_living_space", table, type_="unique")
        op.execute(
            f"ALTER TABLE {table} "
            + _alter_back("price") + ", "
            + _alter_back("rent_extra_costs") + ", "
            + _alter_back("living_space")
        )
        op.create_unique_constraint(
            f"uq_{table}_title_price_city_living_space",
            table,
            ["title", "price", "city", "living_space"],
        )

    op.drop_constraint("uq_property_title_price_city_space", "property", type_="unique")
    op.execute(
        "ALTER TABLE property "
        + _alter_back("price") + ", "
        + _alter_back("space")
    )
    op.create_unique_constraint(
        "uq_property_title_price_city_space",
        "property",
        ["title", "price", "city", "space"],
    )
