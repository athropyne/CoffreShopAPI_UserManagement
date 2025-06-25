"""empty message

Revision ID: 8d63ca36b8ac
Revises: c8ae0e647ae5
Create Date: 2025-06-25 22:45:49.378614

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String

# revision identifiers, used by Alembic.
revision: str = '8d63ca36b8ac'
down_revision: Union[str, Sequence[str], None] = 'c8ae0e647ae5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fake_mails",
        Column("email", String(360), unique=True, nullable=False),
        Column("message", String(360), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("fake_mails")
