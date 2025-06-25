from pathlib import Path

from aiosmtpd.controller import Controller

from src.core.infrastructures import database
from src.core.schemas import fake_mails


class CustomHandler:
    async def handle_DATA(self, server, session, envelope):
        async with database.engine.connect() as connection:
            await connection.execute(
                fake_mails
                .insert()
                .values(email=envelope.rcpt_tos,
                        message=f"""От: {envelope.mail_from}\n
                        Кому: {envelope.rcpt_tos}\nСообщение:\n
                        {envelope.content.decode('utf8').splitlines()[-1]}""")
            )
            await connection.commit()


controller = Controller(CustomHandler(), hostname='localhost', port=1025)
controller.start()
import time

print("SMTP-сервер запущен. Для остановки нажмите Ctrl+C...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Остановка сервиса...")
controller.stop()
