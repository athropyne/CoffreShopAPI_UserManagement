from uuid import UUID

from sqlalchemy import CursorResult, select, true

from src.core.interfaces import BaseSQLRepository
from src.core.schemas import accounts, profiles, verifications
from src.core.types import ID
from src.services.auth.exc import InvalidLoginOrPassword, InvalidVerificationCode
from src.services.users.exc import UserNotFound


class DB_GetUserByLogin(BaseSQLRepository):
    async def __call__(self, login: str):
        stmt = (
            select(
                accounts.c.id,
                accounts.c.password,
                profiles.c.is_admin
            )
            .join(profiles, accounts.c.id == profiles.c.id)
            .where(accounts.c.email == login)
        )
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(stmt)
        result = cursor.mappings().fetchone()
        if not result:
            raise InvalidLoginOrPassword
        return result


class DB_GetVerificationDataByUserId(BaseSQLRepository):
    def verification_stmt(self, client_id: ID):
        return (
            select(
                accounts.c.email,
                verifications.c.code
            )
            .join(verifications, accounts.c.id == verifications.c.user_id)
            .where(accounts.c.id == client_id)
        )

    def confirm_user_stmt(self, client_id: ID):
        delete_verification_code_cte = (
            verifications
            .delete()
            .where(verifications.c.user_id == client_id)
            .cte("delete_verification_code_cte")
        )
        return (
            profiles
            .update()
            .values(verification_status=true())
            .where(profiles.c.id == client_id)
            .add_cte(delete_verification_code_cte)
        )

    async def __call__(self, client_id: ID, verify_code: UUID):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self.verification_stmt(client_id))
            result = cursor.mappings().fetchone()
            if result is None:
                raise UserNotFound(client_id)
            if result["code"] != verify_code:
                raise InvalidVerificationCode
            await connection.execute(self.confirm_user_stmt(client_id))
            await connection.commit()


class DB_GetNewVerificationCode(BaseSQLRepository):
    def stmt(self, user_id: ID, verification_code: UUID):
        update_code_cte = (
            verifications
            .update()
            .values(code=verification_code)
            .where(verifications.c.user_id == user_id)
            .returning(verifications.c.user_id)
            .cte("update_code_cte")
        )
        return (
            select(accounts.c.email)
            .where(accounts.c.id == select(update_code_cte.c.user_id).scalar_subquery())
        )

    async def __call__(self, user_id: ID, verification_code: UUID):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self.stmt(user_id, verification_code))
            user_email = cursor.scalar()
            if user_email is None:
                raise UserNotFound(user_id)
            await connection.commit()
            return user_email
