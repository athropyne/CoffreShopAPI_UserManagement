import asyncio
import uuid
from email.message import EmailMessage
from uuid import UUID

import aiosmtplib
from fastapi import Depends
from pydantic import EmailStr

from src.core.interfaces import BaseService
from src.core.security import PasswordManager, TokenManager, TokenTypes
from src.core.types import ID
from src.services.auth.dto.input import INPUT_AuthData, INPUT_VerifyEmail
from src.services.auth.dto.output import OUTPUT_TokenModel
from src.services.auth.exc import InvalidLoginOrPassword
from src.services.auth.repository import DB_GetUserByLogin, DB_GetVerificationDataByUserId, DB_GetNewVerificationCode
from src.services.users.repsository import DB_GetUserById
from src.services.users.service import SERVICE_SendVerificationCodeToEmail


class SERVICE_Auth(BaseService):
    def __init__(self, repository: DB_GetUserByLogin = Depends()):
        super().__init__()
        self._repository = repository

    async def __call__(self, model: INPUT_AuthData):
        result = await self._repository(model.login)
        if result is not None:
            if not PasswordManager.verify(model.password, result["password"]):
                raise InvalidLoginOrPassword
            access_token = TokenManager.create({"id": str(result["id"]), "admin": result["is_admin"]},
                                               TokenTypes.ACCESS)
            refresh_token = TokenManager.create({"id": str(result["id"])}, TokenTypes.REFRESH)
            return OUTPUT_TokenModel(
                access_token=access_token,
                refresh_token=refresh_token
            )


class SERVICE_Refresh(BaseService):
    def __init__(self,
                 repository: DB_GetUserById = Depends()):
        super().__init__()
        self._repository = repository

    async def __call__(self, refresh_token: str):
        user_id = TokenManager.id(refresh_token)
        user = await self._repository(user_id)
        access_token = TokenManager.create({"id": str(user.id), "admin": user.is_admin},
                                           TokenTypes.ACCESS)
        refresh_token = TokenManager.create({"id": str(user.id)}, TokenTypes.REFRESH)
        return OUTPUT_TokenModel(
            access_token=access_token,
            refresh_token=refresh_token
        )


class SERVICE_VerifyUser(BaseService):
    def __init__(self,
                 repository: DB_GetVerificationDataByUserId = Depends()):
        super().__init__()
        self._repository = repository

    async def __call__(self, client_id: ID, verify_code: UUID):
        await self._repository(client_id, verify_code)


class SERVICE_GetNewVerificationCode(BaseService):
    def __init__(self,
                 repository: DB_GetNewVerificationCode = Depends(),
                 get_user_by_id_command: DB_GetUserById = Depends(),
                 send_mail_service: SERVICE_SendVerificationCodeToEmail = Depends()):
        super().__init__()
        self._repository = repository
        self._get_user_by_id_command = get_user_by_id_command
        self._send_mail_service = send_mail_service

    async def __call__(self, client_id: ID):
        verification_code = uuid.uuid4()
        user_email = await self._repository(client_id, verification_code)
        await self._send_mail_service(None, user_email, verification_code)  # отправка напрямую

