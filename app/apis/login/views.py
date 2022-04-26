from sanic import Request, json
from sanic.views import HTTPMethodView
from services.user import get_session_token
from sanic.exceptions import InvalidUsage
from services.user import get_or_create_user
from utils.mixin.wx_minin import EnsureWXCodeMixin


class LoginResource(HTTPMethodView, EnsureWXCodeMixin):

    async def get(self, request: Request):
        app = request.app
        params = request.args
        code = params.get("code")
        if not code:
            raise InvalidUsage("缺少Code")
        info = await get_session_token(app.config.APP_ID, app.config.APP_SECRET, code)
        await get_or_create_user(info['openid'])
        await self.set_wx_code(app.ctx.redis, code, info)
        return json(info)
