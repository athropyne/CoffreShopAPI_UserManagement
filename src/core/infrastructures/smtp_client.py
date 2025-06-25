from email.message import EmailMessage

import aiosmtplib
import loguru
from pydantic import EmailStr

from src.core import config


class SMTPClient:
    async def __call__(self, recipient: EmailStr, subject: str, msg: str):
        message = EmailMessage()
        message["From"] = config.settings.EMAIL_ADDRESS
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(msg)
        try:
            await aiosmtplib.send(message, hostname="fake_smtp_server_app", port=config.settings.SMTP_SERVER_PORT)
        except aiosmtplib.errors.SMTPConnectError:
            loguru.logger.error(f"Почта не отправлена. Отсутствует соединение с удаленным сервисом\n {message}")
