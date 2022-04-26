from sanic import Request
from sanic.views import HTTPMethodView
from services.order import create_order
from utils.mixin.wx_minin import EnsureWXCodeMixin
from utils.responses.response_container import make_response


class OrderResource(HTTPMethodView, EnsureWXCodeMixin):

    async def post(self, request: Request):
        app = request.app
        params = request.json

        openid = await self.ensure_wx_code(app.ctx.redis, params['code'])
        info = await create_order(
            questionnaire_id=params['questionnaire_id'],
            openid=openid,
            app_id=app.config.APP_ID,
            api_key=app.config.API_KEY,
            cert_path=app.config.CERT_PATH,
            key_path=app.config.KEY_PATH,
            mchid=app.config.MERC_ID,
            price=app.config.ORDER_PRICE,
            notify_url=app.config.NOTIFY_URL,
            desc=app.config.ORDER_DESC,
        )

        return make_response(info)

    async def get(self, request: Request):
        ...
