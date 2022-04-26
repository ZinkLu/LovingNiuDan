from aioredis import create_redis
from aioredis.errors import RedisError

from utils.responses.response_container import make_response

from . import app

redis_cli = None


@app.before_server_start
async def bind_redis(app, loop):
    global redis_cli
    redis_client = await create_redis(**app.config.REDIS_URL)
    redis_cli = redis_client
    app.ctx.redis = redis_client


@app.exception(RedisError)
async def redis_exception(r, e: RedisError):
    return make_response(message="error on redis", status=500, code=500)
