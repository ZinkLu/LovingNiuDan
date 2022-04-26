from contextlib import asynccontextmanager

from inits.init_db import session


def commit(fn):

    async def wrapper(*args, **kwargs):
        async with safe_commit():
            return await fn(*args, **kwargs)

    return wrapper


@asynccontextmanager
async def safe_commit():
    try:
        async with session.begin():
            yield session
    except BaseException as e:
        await session.rollback()
        raise e
