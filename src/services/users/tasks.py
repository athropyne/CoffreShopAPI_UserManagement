from src.core.infrastructures.taskiq import broker


@broker.task
async def test():
    pass
