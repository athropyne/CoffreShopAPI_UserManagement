"""empty message

Revision ID: c1d6395cdd73
Revises: 
Create Date: 2025-06-25 17:12:43.695829

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, false, func, UUID

from src.core.schemas import accounts

# revision identifiers, used by Alembic.
revision: str = 'c1d6395cdd73'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "accounts",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("email", String(360), unique=True, nullable=False),
        Column("password", String(100), nullable=False)
    )

    op.create_table(
        "profiles",
        Column("id", ForeignKey(accounts.c.id, ondelete="CASCADE"), primary_key=True),
        Column("first_name", String(50), nullable=True),
        Column("last_name", String(50), nullable=True),
        Column("verification_status", Boolean, nullable=False, default=false()),
        Column("is_admin", Boolean, nullable=False, default=false()),
        Column("created_at", DateTime, nullable=False, default=func.now())
    )

    op.create_table(
        "verifications",
        Column("user_id", ForeignKey(accounts.c.id, ondelete="CASCADE"), nullable=False, primary_key=True),
        Column("code", UUID, nullable=False)
    )


def downgrade():
    op.drop_table('verifications')
    op.drop_table('profiles')
    op.drop_table('accounts')
