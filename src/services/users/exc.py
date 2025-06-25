from fastapi import HTTPException
from pydantic import EmailStr

from src.core.exc import AlreadyExists, NotFound
from src.core.types import ID


class UserAlreadyExists(AlreadyExists):
    def __init__(self,
                 email: EmailStr):
        super().__init__(detail=f"пользователь с почтой {email} уже зарегистрирован")


class UserNotFound(NotFound):
    def __init__(self,
                 user_id: ID):
        super().__init__(detail=f"пользователь с ID {user_id} не найден")
