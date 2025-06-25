from fastapi import Depends
from fastapi.params import Path

from src.core.exc import AccessDenied
from src.core.security import TokenManager
from src.core.types import ID


async def is_admin(
        payload: dict = Depends(TokenManager.decode)
):
    _is_admin = payload["admin"]
    if not _is_admin:
        raise AccessDenied("У вас нет прав на это действие")
    return payload


async def is_owner_or_admin(
        user_id: ID = Path(..., alias="id", description="ID Пользователя"),
        payload: dict = Depends(TokenManager.decode)
):
    try:
        _is_admin = await is_admin(payload)
    except AccessDenied as e:
        if ID(payload["id"]) != user_id:
            raise
        return payload
