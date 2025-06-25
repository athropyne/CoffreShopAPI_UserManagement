from pydantic import BaseModel, Field, EmailStr


class INPUT_CreateUser(BaseModel):
    email: EmailStr = Field(..., description="почта")
    password: str = Field(..., max_length=100, description="пароль")
    first_name: str | None = Field(None, max_length=50, description="имя")
    last_name: str | None = Field(None, max_length=50, description="фамилия")


class INPUT_UpdateProfile(BaseModel):
    first_name: str | None = Field(None, max_length=50, description="имя")
    last_name: str | None = Field(None, max_length=50, description="фамилия")
