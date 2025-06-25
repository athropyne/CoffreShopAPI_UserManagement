from uuid import UUID

from fastapi import APIRouter, Depends, Body
from pydantic import EmailStr
from starlette import status

from src.core import utils
from src.core.security import TokenManager
from src.core.types import ID
from src.services.auth.dto.input import INPUT_AuthData
from src.services.auth.dto.output import OUTPUT_TokenModel
from src.services.auth.service import SERVICE_Auth, SERVICE_Refresh, SERVICE_VerifyUser, SERVICE_GetNewVerificationCode

auth_router = APIRouter(prefix="/auth", tags=["Безопасность"])


@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Аутентифицироваться",
    description="""
    Функция аутентификации пользователя. 
    При валидных данных возвращает `access_token` - токен доступа и `refresh_token` - токен обновления.
    При неверных данных вернет ошибку 400.
    """,
    response_model=OUTPUT_TokenModel,
)
async def auth(
        model: INPUT_AuthData = Depends(utils.convert_auth_data),
        service: SERVICE_Auth = Depends()
):
    return await service(model)


@auth_router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Обновить токен доступа",
    description="""
    Функция обновления токена доступа и токена обновления.
    """
)
async def refresh(
        refresh_token: str = Body(...),
        service: SERVICE_Refresh = Depends()
):
    return await service(refresh_token)


@auth_router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
    summary="Верифицировать аккаунт",
    description="""
    Функция подтверждает аккаунт с помощью кода отправленного на email при регистрации
    """
)
async def verify(
        verification_code: UUID = Body(...),
        client_id: ID = Depends(TokenManager.id),
        service: SERVICE_VerifyUser = Depends()
):
    await service(client_id, verification_code)


@auth_router.post(
    "/code",
    status_code=status.HTTP_200_OK,
    summary="Получить код верификации",
    description="""
    Функция отправляет код верификации на указанный email,
    если он не был получен при регистрации (хотя должен).
    В случае успеха вернет код 200
    """
)
async def code(
        client_id: ID = Depends(TokenManager.id),
        service: SERVICE_GetNewVerificationCode = Depends()
):
    await service(client_id)



