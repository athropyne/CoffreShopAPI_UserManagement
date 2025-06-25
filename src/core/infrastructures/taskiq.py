from arq import create_pool
from arq.connections import RedisSettings, ArqRedis

from src.core import config

REDIS_SETTINGS = RedisSettings.from_dsn(config.settings.REDIS_DSN)


class TaskManager:
    def __init__(self, redis_dsn: str):
        self.REDIS_SETTINGS = RedisSettings.from_dsn(redis_dsn)
        self.pool = None

    def __call__(self) -> ArqRedis:
        return self.pool

    async def init(self):
        self.pool = await create_pool(self.REDIS_SETTINGS)



