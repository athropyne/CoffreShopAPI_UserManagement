import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, DateTime, Boolean, UUID, true, false, func

metadata = MetaData()

accounts = Table(
    "accounts",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("email", String(360), unique=True, nullable=False),
    Column("password", String(100), nullable=False)
)

profiles = Table(
    "profiles",
    metadata,
    Column("id", ForeignKey(accounts.c.id, ondelete="CASCADE"), primary_key=True),
    Column("first_name", String(50), nullable=True),
    Column("last_name", String(50), nullable=True),
    Column("verification_status", Boolean, nullable=False, default=false()),
    Column("is_admin", Boolean, nullable=False, default=false()),
    Column("created_at", DateTime, nullable=False, default=func.now())
)

verifications = Table(
    "verifications",
    metadata,
    Column("user_id", ForeignKey(accounts.c.id, ondelete="CASCADE"), nullable=False, primary_key=True),
    Column("code", UUID, nullable=False)
)


fake_mails = Table(
    "fake_mails",
    metadata,
    Column("email", String(360), unique=True, nullable=False),
    Column("message", String(360), nullable=False),
)
