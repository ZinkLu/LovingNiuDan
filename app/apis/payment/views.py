from sanic import Request
from sanic.exceptions import InvalidUsage, NotFound
from sanic.views import HTTPMethodView

from inits.init_logger import logger
from services.order import get_paying_order_by_id
from services.payment import get_payment_info, update_payment_info, get_payment_status
from utils.mixin.wx_minin import EnsureWXCodeMixin
from utils.responses.response_container import make_response


class PaymentResource(HTTPMethodView, EnsureWXCodeMixin):

    async def post(self, request: Request):
        app = request.app
        params = request.json

        await self.ensure_wx_code(app.ctx.redis, params['code'])

        if not (order_id := params.get("order_id")):
            raise InvalidUsage("订单id缺失")

        order = await get_paying_order_by_id(order_id)

        if not order:
            raise NotFound("未找到订单")

        info = await get_payment_info(
            app_id=app.config.APP_ID,
            api_key=app.config.API_KEY,
            cert_path=app.config.CERT_PATH,
            key_path=app.config.KEY_PATH,
            mchid=app.config.MERC_ID,
            prepay_id=order.wx_pay_no,
        )

        return make_response(info)

    async def get(self, request: Request):
        ...


class PaymentCallback(HTTPMethodView):

    async def post(self, request: Request):
        """
        {
            'id': '45544e27-e2a5-5ffe-ae9f-3c15d6ebc8dd',
            'create_time': '2021-08-09T23:18:31+08:00',
            'resource_type': 'encrypt-resource',
            'event_type': 'TRANSACTION.SUCCESS',
            'summary': '支付成功',
            'resource': {
                'original_type': 'transaction',
                'algorithm': 'AEAD_AES_256_GCM',
                'ciphertext':
                'fgFgPnlStmXAuAYcFuYzx/9iQ69txa0jxRHIty2bcBJUGW1zqydQBIKw6lLJbYdMbtIgBd9Yv+DVrtt1Zyat/qq8Wo4QAN77qvAiZd6+bTXI/RsSSdcFK0iQLu5Sivg6Xuy/oc+xxQq8NxszRxyIHKT/lr9fYnV/wziZ7qeJyZ3YlS0TT+4VapXW/M8RU0d1Hq4XqLhlaSYSPc475Bu0xHN2U5PIKPS1qBNtKPbHuPRK4vEBV4JlzbKZzXncl/Y61T0KqR1Ya2ToaMl6UOeapM6aC93uPxano/UFmH5IrxZXxJcyoYF4AJLtHOB8Gu0KGQ94XR2dyhRL9qBaPG5gvWJxv+UJP9pXraOTafrDkdFQsP6wTgsWxDZM/L0NuHfbU78UF26dUPo4LWE0i7Mmel5bOFVC0LKgg1/596LKEE4r87/AsnLPAgMKOs7Cv2jjneCuhOaaQqwSI76bAuhemM6raeII0Xbtj1KGLxmnW+A2q2g4UjEb9a9iHJfzDSkuPSRSMc6mib13mWydPnOgHZ++Xqel6WkTeGUUT7i8PHaE9EWlGJKyOtwbiRQBktMC6DBR',
                'associated_data': 'transaction',
                'nonce': 'bBeHQ1OU6UCp'
            }
        }
        """
        app = request.app
        params = request.json
        logger.info(f"收到微信的回调，{params} 正在更新状态", )

        await update_payment_info(app_id=app.config.APP_ID,
                                  api_key=app.config.API_KEY,
                                  cert_path=app.config.CERT_PATH,
                                  key_path=app.config.KEY_PATH,
                                  mchid=app.config.MERC_ID,
                                  call_back_message=params)
        return make_response(dict())


class PaymentCheck(HTTPMethodView):

    async def get(self, request: Request):
        params = request.json
        if not any((params.get("order_id"), params.get("questionnaire_id"))):
            raise InvalidUsage("either order_id and questionnaire_id is required")

        status = await get_payment_status(params.get("order_id"), params.get("questionnaire_id"))

        return make_response(dict(status=status))
