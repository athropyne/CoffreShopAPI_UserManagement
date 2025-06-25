import datetime

from pydantic import BaseModel, Field

from src.core.types import ID


class OUTPUT_FullUserInfo(BaseModel):
    id: ID = Field(description="Идентификатор пользователя")
    first_name: str | None = Field(description="Имя")
    last_name: str | None = Field(description="Фамилия")
    verification_status: bool = Field(description="Верифицирован или нет")
    is_admin: bool = Field(description="Администратор или нет")
    created_at: datetime.datetime = Field(description="Дата регистрации")
