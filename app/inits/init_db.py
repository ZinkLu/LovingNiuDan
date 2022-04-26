from contextvars import ContextVar

import ujson
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from configs.db_configs import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from utils.responses.response_container import make_response
from . import app
from .init_logger import logger

_base_model_session_ctx = ContextVar("session")


class Proxy:
    empty = object()

    def __init__(self, wrappee: ContextVar):
        self.wrappee = wrappee

    def __getattr__(self, attr):
        if attr in ("__token"):
            return super().__getattr__(attr)

        if self.wrappee.get(self.empty) is self.empty:
            raise RuntimeError("a session only can be get under a request life cycle")
        return getattr(self.wrappee.get(), attr)

    def _start_mock_session(self):
        session = sessionmaker(bind, AsyncSession, expire_on_commit=False)()
        session_ctx_token = _base_model_session_ctx.set(session)
        self.__token = session_ctx_token

    def _close_mock_session(self):
        from asyncio import get_event_loop, run_coroutine_threadsafe
        loop = get_event_loop()
        run_coroutine_threadsafe(self.close(), loop)
        _base_model_session_ctx.reset(self.__token)


session = Proxy(_base_model_session_ctx)

bind = create_async_engine(
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    json_deserializer=ujson.loads,
    json_serializer=ujson.dumps,
    pool_size=10,
    pool_recycle=60 * 15,  # 设置pool内的链接不超过15分钟
)


@app.middleware("request")
async def inject_session(request):
    request.ctx.session = sessionmaker(bind, AsyncSession, expire_on_commit=False)()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)


@app.middleware("response")
async def close_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        try:
            await session.commit()
        except Exception as e:
            logger.exception(e)
            await session.rollback()
            return make_response(message='db error', status=500, code=500)
        finally:
            await request.ctx.session.close()
            _base_model_session_ctx.reset(request.ctx.session_ctx_token)


@app.before_server_start
async def create_tables(app, loop):
    async with bind.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@app.exception(SQLAlchemyError)
async def handle_db_exception(r, e: SQLAlchemyError):
    logger.error("a db exception has occurred, check: ")
    logger.error(e)
    return make_response(message="数据库异常", status=500, code=500)


from models import Base, BaseModel, PaymentModel, PrintTaskModel, QuestionnaireModel, UserModel  # noqa
