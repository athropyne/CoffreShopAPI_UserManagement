import loguru
from arq import ArqRedis

from src.core.infrastructures import Database, database, task_manager, TaskManager


class D:
    @staticmethod
    def database() -> Database:
        return database

    @staticmethod
    def logger() -> loguru.logger:
        return loguru.logger

    @staticmethod
    def task_manager() -> TaskManager:
        return task_manager
