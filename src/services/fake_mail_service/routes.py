from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import EmailStr
from sqlalchemy import CursorResult, select
from starlette import status

from src.core.dependencies import D
from src.core.infrastructures import Database
from src.core.schemas import fake_mails

email_router = APIRouter(prefix="/mail", tags=["Фальшивый email сервис"])


@email_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Получить почту",
    description="""
    Функция имитирует почтовый клиент.
    Это тестовая функция и в реальном приложении ее не будет. 
    Нужно "войти" в свою почту, указанную при регистрации и получить письмо с верификационным кодом
    """
)
async def get_mail(
        email: EmailStr,
        database: Database = Depends(D.database)
):
    async with database.engine.connect() as connection:
        cursor: CursorResult = await connection.execute(
            select(fake_mails.c.message)
            .where(fake_mails.c.email == email)
        )
        return cursor.mappings().fetchall()
