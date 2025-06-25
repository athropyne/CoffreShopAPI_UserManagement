from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.core.dependencies import D
from src.core.infrastructures.smtp_client import SMTPClient
from src.core.infrastructures.taskiq import REDIS_SETTINGS
from src.services.auth.routes import auth_router
from src.services.fake_mail_service.routes import email_router
from src.services.users.repsository import DB_DeleteNotConfirmedUser
from src.services.users.routes import user_router
from src.services.users.service import SERVICE_SendVerificationCodeToEmail


class WorkerSettings:
    functions = [
        DB_DeleteNotConfirmedUser().__call__,
        SERVICE_SendVerificationCodeToEmail(SMTPClient()).__call__
    ]
    redis_settings = REDIS_SETTINGS


@asynccontextmanager
async def lifespan(app: FastAPI):
    task_manager = D.task_manager()
    await task_manager.init()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="CoffeeShopUserManagementService"
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(email_router)
