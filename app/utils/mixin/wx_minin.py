import ujson
from aioredis import Redis
from sanic.exceptions import InvalidUsage


class EnsureWXCodeMixin:

    async def ensure_wx_code(self, redis_cli, code) -> str:
        if not code:
            raise InvalidUsage(message='code不存在')

        res = await redis_cli.get(code)
        if not res:
            raise InvalidUsage(message="code已过期请重新获取")

        openid = ujson.loads(res)['openid']
        return openid

    async def set_wx_code(self, redis_cli: Redis, code: str, info: dict):
        await redis_cli.set(code, ujson.dumps(info), expire=5 * 60, exist=Redis.SET_IF_NOT_EXIST)
