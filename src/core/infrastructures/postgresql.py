from loguru import logger
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


class Database:
    def __init__(self,
                 user: str,
                 password: str,
                 socket: str,
                 dbname: str,
                 enable_logs: bool = True
                 ):
        self.engine = create_async_engine(
            f"postgresql+asyncpg://{user}:{password}@{socket}/{dbname}",
            echo=True if enable_logs else False)

    async def init(self, metadata: MetaData):
        async with self.engine.connect() as connection:
            await connection.run_sync(metadata.drop_all)
            await connection.run_sync(metadata.create_all)
            await connection.commit()
        await self.engine.dispose()
        logger.info("PostgreSQL проинициализирована")

    async def dispose(self):
        await self.engine.dispose()

    def __call__(self) -> AsyncEngine:
        return self.engine
