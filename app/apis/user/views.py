from sanic import Request
from sanic.views import HTTPMethodView

from services.user import get_or_create_user
from utils.mixin.wx_minin import EnsureWXCodeMixin
from utils.responses.response_container import make_response


class UserResource(HTTPMethodView, EnsureWXCodeMixin):

    async def post(self, request: Request):
        app = request.app
        params = request.json
        code = params.get("code")
        openid = await self.ensure_wx_code(app.ctx.redis, code)

        # encrypted_data = params.get("encryptedData")
        # iv = params.get("iv")
        user_info = params.get('userInfo')
        # user_info = params.get("signature")

        res = await get_or_create_user(openid,
                                       nickname=user_info['nickName'],
                                       avatar_url=user_info['avatarUrl'],
                                       **user_info)

        return make_response(res.id)
