from typing import Optional
from models.order import OrderModel
from models.user import UserModel
from models.questionnaire import QuestionnaireModel
from utils.db_utils.commit import commit
from utils.exceptions.exception import ServiceException
from utils.wx_client.client import WxPayClient


@commit
async def create_order(
    questionnaire_id: int,
    openid: str,
    app_id: str,
    api_key: str,
    key_path: str,
    cert_path: str,
    mchid: str,
    price: int,
    notify_url: str,
    desc: str = '',
) -> int:
    questionnaire = await QuestionnaireModel.get_by_id(questionnaire_id)
    if not questionnaire:
        raise ServiceException("未找到记录", 404)

    order = await OrderModel.create(
        questionnaire_id=questionnaire.id,
        user_id=questionnaire.user_id,
        price=price,
    )

    async with WxPayClient(
            app_id=app_id,
            mchid=mchid,
            key_path=key_path,
            api_key=api_key,
            cert_path=cert_path,
    ) as client:
        order_info = await client.make_order(order.out_trade_no, price, openid, notify_url, desc)

    if not (wx_order_no := order_info.get("prepay_id")):
        raise ServiceException("微信下单失败！", 502)

    user = await UserModel.create_by_wx_app_openid(openid)
    order = await OrderModel.create(
        questionnaire_id=questionnaire_id,
        user_id=user.id,
        price=price,
        wx_pay_no=wx_order_no,
    )

    return order.id


async def get_order_by_id(order_id: int) -> Optional[OrderModel]:
    return await OrderModel.get_by_id(order_id)


async def get_paying_order_by_id(order_id: int) -> Optional[OrderModel]:
    """获取待支付的订单"""
    order = await get_order_by_id(order_id)
    if not order:
        return

    if await order.is_paid_success():
        raise ServiceException("该订单已经支付成功")

    return order
