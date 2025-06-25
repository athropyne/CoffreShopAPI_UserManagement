"""empty message

Revision ID: c8ae0e647ae5
Revises: c1d6395cdd73
Create Date: 2025-06-25 17:26:44.136122

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import true

from src.core.config import settings
from src.core.schemas import accounts, profiles
from src.core.security import PasswordManager

# revision identifiers, used by Alembic.
revision: str = 'c8ae0e647ae5'
down_revision: Union[str, Sequence[str], None] = 'c1d6395cdd73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.bulk_insert(
        accounts,
        [
            {'email': settings.ADMIN_LOGIN, 'password': PasswordManager.hash(settings.ADMIN_PASSWORD)}
        ]
    )
    conn = op.get_bind()
    admin_id = conn.execute(
        sa.text(f"SELECT id FROM accounts WHERE email = '{settings.ADMIN_LOGIN}'")
    ).scalar()

    if admin_id:
        op.bulk_insert(
            profiles,
            [
                {
                    'id': admin_id,
                    'verification_status': True,
                    'is_admin': True
                }
            ]
        )


def downgrade() -> None:
    conn = op.get_bind()

    admin_id = conn.execute(
        sa.text(f"SELECT id FROM accounts WHERE email = '{settings.ADMIN_LOGIN}'")
    ).scalar()

    if admin_id:
        conn.execute(
            sa.text(f"DELETE FROM profiles WHERE id = {admin_id}")
        )

        conn.execute(
            sa.text(f"DELETE FROM accounts WHERE email = '{settings.ADMIN_LOGIN}'")
        )
