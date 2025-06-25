from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')

    # server
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 10000

    # admin
    ADMIN_LOGIN: str = "admin@example.com"
    ADMIN_PASSWORD: str = "string"

    # databases
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "CoffeeShopUserManagement"
    POSTGRES_SOCKET: str = "localhost"
    POSTGRES_LOGS: bool = True

    # token config
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_HOURS: int = 24 * 15
    TOKEN_SECRET_KEY: str = "abracadabra"

    # system email
    EMAIL_ADDRESS: str = "support@local"
    SMTP_SERVER_HOST: str = "localhost"
    SMTP_SERVER_PORT: int = 1025

    # redis
    REDIS_DSN: str = "redis://127.0.0.1:6379"


settings = Settings()
