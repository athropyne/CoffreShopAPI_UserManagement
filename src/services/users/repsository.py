from uuid import UUID

from asyncpg import UniqueViolationError
from sqlalchemy import CursorResult, Executable, select, Select, Update, Delete, exists, false, true
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.dml import ReturningInsert

from src.core.interfaces import BaseSQLRepository
from src.core.schemas import accounts, profiles, verifications
from src.core.types import ID
from src.services.users.dto.input import INPUT_CreateUser, INPUT_UpdateProfile
from src.services.users.dto.output import OUTPUT_FullUserInfo
from src.services.users.exc import UserAlreadyExists, UserNotFound


class DB_CreateUser(BaseSQLRepository):
    def stmt(self, model: INPUT_CreateUser, verification_code: UUID) -> ReturningInsert:

        account_cte = (
            accounts
            .insert()
            .values(
                email=model.email,
                password=model.password
            )
            .returning(accounts.c.id)
            .cte("accounts_cte")
        )

        verification_cte = (
            verifications
            .insert()
            .values(
                user_id=select(account_cte.c.id).scalar_subquery(),
                code=verification_code
            )
            .cte("verification_cte")
        )
        return (
            profiles
            .insert()
            .values(
                id=select(account_cte.c.id).scalar_subquery(),
                first_name=model.first_name,
                last_name=model.last_name,
            )
            .returning(profiles)
            .add_cte(verification_cte)
        )

    async def __call__(self, model: INPUT_CreateUser, verification_code: UUID):
        async with self.engine.connect() as connection:
            try:
                cursor: CursorResult = await connection.execute(self.stmt(model, verification_code))
                await connection.commit()
                result = cursor.mappings().fetchone()
                return OUTPUT_FullUserInfo(**result)
            except IntegrityError as e:
                if isinstance(e.orig.__cause__, UniqueViolationError):
                    raise UserAlreadyExists(model.email)


class DB_GetUserList(BaseSQLRepository):
    def stmt(self, skip: int, limit: int) -> Select:
        return (
            select(profiles)
            .offset(skip)
            .limit(limit)
        )

    async def __call__(self, skip: int, limit: int):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self.stmt(skip, limit))
            result = cursor.mappings().fetchall()
            return [OUTPUT_FullUserInfo(**item) for item in result]



class DB_GetUserById(BaseSQLRepository):
    def stmt(self, user_id: ID) -> Select:
        return (
            select(profiles)
            .where(profiles.c.id == user_id)
        )

    async def __call__(self, user_id: ID):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self.stmt(user_id))
            result = cursor.mappings().fetchone()
            if result is None:
                raise UserNotFound(user_id)
            return OUTPUT_FullUserInfo(**result)


class DB_UpdateUserById(BaseSQLRepository):
    def stmt(self,
             user_id: ID,
             model: INPUT_UpdateProfile) -> Update:
        return (
            profiles
            .update()
            .values(model.model_dump(exclude_none=True))
            .where(profiles.c.id == user_id)
            .returning(profiles)
        )

    async def __call__(self,
                       user_id: ID,
                       model: INPUT_UpdateProfile):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self.stmt(user_id, model))
            if cursor.rowcount != 1:
                raise UserNotFound(user_id)
            await connection.commit()
            result = cursor.mappings().fetchone()
            return OUTPUT_FullUserInfo(**result)


class DB_DeleteUser(BaseSQLRepository):
    def stmt(self, user_id: ID) -> Delete:
        return (
            accounts
            .delete()
            .where(accounts.c.id == user_id)
        )

    async def __call__(self, user_id: ID):
        async with self.engine.connect() as connection:
            cursor: CursorResult = await connection.execute(self.stmt(user_id))
            if cursor.rowcount != 1:
                raise UserNotFound(user_id)
            await connection.commit()


class DB_DeleteNotConfirmedUser(BaseSQLRepository):
    def stmt(self, user_id: ID):
        return (
            accounts
            .delete()
            .where(accounts.c.id == user_id)
            .where(profiles.c.verification_status == false())
        )

    async def __call__(self, ctx, user_id: ID):
        def stmt(_user_id: ID):
            return (
                accounts
                .delete()
                .where(accounts.c.id == _user_id)
                .where(profiles.c.verification_status == false())
            )

        async with self.engine.connect() as connection:
            await connection.execute(stmt(user_id))
            await connection.commit()
