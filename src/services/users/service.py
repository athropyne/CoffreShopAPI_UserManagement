import uuid
from datetime import timedelta
from logging import Logger

import aiosmtplib
from arq import ArqRedis
from fastapi import Depends
from pydantic import EmailStr

from src.core.dependencies import D
from src.core.infrastructures import TaskManager
from src.core.infrastructures.smtp_client import SMTPClient
from src.core.interfaces import BaseService
from src.core.security import PasswordManager
from src.core.types import ID
from src.services.users.dto.input import INPUT_CreateUser, INPUT_UpdateProfile
from src.services.users.repsository import (
    DB_CreateUser,
    DB_GetUserById,
    DB_UpdateUserById,
    DB_DeleteUser,
    DB_GetUserList, DB_DeleteNotConfirmedUser
)


class SERVICE_SendVerificationCodeToEmail(BaseService):
    def __init__(self,
                 smtp_client: SMTPClient = Depends()):
        super().__init__()
        self._smtp_client = smtp_client

    async def __call__(self, ctx, recipient: EmailStr, verification_code: uuid.UUID):
        await self._smtp_client(recipient, subject="verification code", msg=f"Ваш код проверки {verification_code}")


class SERVICE_CreateUser(BaseService):
    def __init__(self,
                 repository: DB_CreateUser = Depends(),
                 verification_service: SERVICE_SendVerificationCodeToEmail = Depends(),
                 logger: Logger = Depends(D.logger),
                 task_manager: TaskManager = Depends(D.task_manager)
                 ):
        super().__init__()
        self._repository = repository
        self._verification_service = verification_service
        self._logger = logger
        self._task_manager_pool = task_manager.pool

    async def __call__(self, model: INPUT_CreateUser):
        verification_code = uuid.uuid4()
        model.password = PasswordManager.hash(model.password)
        result = await self._repository(model, verification_code)
        await self._task_manager_pool.enqueue_job(
            "SERVICE_SendVerificationCodeToEmail.__call__",
            recipient=model.email,
            verification_code=verification_code
        )  # попытка отправить email с кодом

        await self._task_manager_pool.enqueue_job(
            "DB_DeleteNotConfirmedUser.__call__",
            result.id,
            _defer_by=timedelta(days=2)
        )  # удалить пользователя если он 2 дня не подтверждает мыло
        return result


class SERVICE_GetMe(BaseService):
    def __init__(self,
                 repository: DB_GetUserById = Depends()):
        super().__init__()
        self._repository = repository

    async def __call__(self, client_id: ID):
        result = await self._repository(client_id)
        return result


class SERVICE_GetUserList(BaseService):
    def __init__(self,
                 repository: DB_GetUserList = Depends()):
        super().__init__()
        self._repository = repository

    async def __call__(self,
                       client_id: ID,
                       skip: int,
                       limit: int):
        result = await self._repository(skip, limit)
        return result


class SERVICE_GetUserById(BaseService):
    def __init__(self,
                 repository: DB_GetUserById = Depends()):
        super().__init__()
        self._repository = repository

    async def __call__(self, client_id: ID, user_id: ID):
        result = await self._repository(user_id)
        return result


class SERVICE_UpdateUserById(BaseService):
    def __init__(self,
                 repository: DB_UpdateUserById = Depends()):
        super().__init__()
        self._repository = repository

    async def __call__(self,
                       client_id: ID,
                       user_id: ID,
                       model: INPUT_UpdateProfile):
        result = await self._repository(user_id, model)
        return result


class SERVICE_DeleteUser(BaseService):
    def __init__(self,
                 repository: DB_DeleteUser = Depends()):
        super().__init__()
        self._repository = repository

    async def __call__(self, client_id: ID, user_id: ID):
        await self._repository(user_id)
