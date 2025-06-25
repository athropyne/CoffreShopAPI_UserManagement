# from src.app import TaskManager
from src.core.infrastructures.postgresql import Database

from src.core.infrastructures.postgresql import Database
from src.core.config import settings
from src.core.infrastructures.taskiq import TaskManager

database = Database(
    settings.POSTGRES_USER,
    settings.POSTGRES_PASSWORD,
    settings.POSTGRES_SOCKET,
    settings.POSTGRES_DB,
    settings.POSTGRES_LOGS,
)

task_manager = TaskManager(settings.REDIS_DSN)

