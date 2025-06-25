from fastapi import APIRouter, Depends, Path
from starlette import status

from src.core.security import TokenManager
from src.core.types import ID
from src.services.users.dependencies import is_admin, is_owner_or_admin
from src.services.users.dto.input import INPUT_CreateUser, INPUT_UpdateProfile
from src.services.users.dto.output import OUTPUT_FullUserInfo
from src.services.users.service import SERVICE_GetUserList, SERVICE_GetMe, SERVICE_CreateUser, SERVICE_GetUserById, \
    SERVICE_UpdateUserById, SERVICE_DeleteUser

user_router = APIRouter(prefix="/users", tags=["Пользователи"])


@user_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Зарегистрироваться",
    description="""
    Создает нового пользователя.
    При успехе возвращает его ID.
    При неудаче вернет код 400
    """,
    response_model=OUTPUT_FullUserInfo
)
async def create(
        model: INPUT_CreateUser,
        service: SERVICE_CreateUser = Depends()
):
    return await service(model)


@user_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Получить текущего пользователя",
    description="""
    Функция возвращает текущего пользователя
    """,
    response_model=OUTPUT_FullUserInfo
)
async def get_my_info(
        client_id: ID = Depends(TokenManager.id),
        service: SERVICE_GetMe = Depends()
):
    return await service(client_id)


@user_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Получить список пользователей",
    description="""
    Функция возвращает список пользователей.
    Доступно только для администратора
    """,
    response_model=list[OUTPUT_FullUserInfo],
    dependencies=[Depends(is_admin)]
)
async def get_user_list(
        skip: int = 0,
        limit: int = 50,
        client_id: ID = Depends(TokenManager.id),
        service: SERVICE_GetUserList = Depends()
):
    return await service(client_id, skip, limit)


@user_router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Получить пользователя по ID",
    description="""
    Функция возвращает информацию пользователя по его ID.
    Доступно только для администратора.
    Если пользователя не существует вернет код 404
    """,
    response_model=OUTPUT_FullUserInfo,
    dependencies=[Depends(is_admin)]
)
async def get_user_by_id(
        user_id: ID = Path(..., alias="id", description="ID Пользователя"),
        client_id: ID = Depends(TokenManager.id),
        service: SERVICE_GetUserById = Depends()
):
    return await service(client_id, user_id)


@user_router.patch(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Обновить данные пользователя",
    description="""
    Функция частично обновляет данные пользователя.
    Доступно только для администратора или владельца аккаунта.
    Возвращает обновленного пользователя
    """,
    response_model=OUTPUT_FullUserInfo,
    dependencies=[Depends(is_owner_or_admin)]
)
async def update_user(
        model: INPUT_UpdateProfile,
        user_id: ID = Path(..., alias="id", description="ID Пользователя"),
        client_id: ID = Depends(TokenManager.id),
        service: SERVICE_UpdateUserById = Depends()
):
    return await service(client_id, user_id, model)


@user_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
    description="""
    Функция удаляет пользователя по ID.
    Доступно только для администратора.
    Если пользователь не найден вернет статус 404
    """,
    response_model=None,
    dependencies=[Depends(is_admin)]
)
async def delete_user(
        user_id: ID = Path(..., alias="id", description="ID Пользователя"),
        client_id: ID = Depends(TokenManager.id),
        service: SERVICE_DeleteUser = Depends()
):
    await service(client_id, user_id)
