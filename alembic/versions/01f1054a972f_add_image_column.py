"""add image column

Revision ID: 01f1054a972f
Revises: b7e4c91d2a6f
Create Date: 2026-09-03 13:30:17.580968

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '01f1054a972f'
down_revision: Union[str, Sequence[str], None] = 'b7e4c91d2a6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    for table in ("houses", "apartments", "property"):
        op.add_column(table, sa.Column(
            "images", postgresql.ARRAY(sa.Text()),
            nullable=False, server_default="{}",
        ))


def downgrade():
    for table in ("houses", "apartments", "property"):
        op.drop_column(table, "images")
