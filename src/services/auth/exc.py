from src.core.exc import ClientError


class InvalidLoginOrPassword(ClientError):
    def __init__(self):
        super().__init__(detail="Неверный логин или пароль")


class InvalidVerificationCode(ClientError):
    def __init__(self):
        super().__init__(detail="Неверный код верификации")
