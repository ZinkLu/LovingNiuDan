from sanic import Request
from sanic.views import HTTPMethodView
from utils.mixin.wx_minin import EnsureWXCodeMixin
from utils.responses.response_container import make_response


class ConfigResource(HTTPMethodView, EnsureWXCodeMixin):

    async def get(self, request: Request):
        app = request.app  # type Sanic
        keys = ["ORDER_DESC", "ORDER_PRICE"]
        configs = {key: app.config[key] for key in keys}
        return make_response(data=configs)
