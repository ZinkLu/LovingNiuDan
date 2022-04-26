from datetime import datetime

import ujson

from inits.init_logger import logger
from models.order import OrderModel
from models.questionnaire import QuestionnaireModel
from models.payment import PaymentModel
from models.user import UserModel
from utils.db_utils.commit import commit
from utils.wx_client.client import WxPayClient


async def get_payment_info(
    app_id,
    api_key,
    cert_path,
    key_path,
    mchid,
    prepay_id,
) -> dict:
    async with WxPayClient(
            app_id=app_id,
            mchid=mchid,
            key_path=key_path,
            api_key=api_key,
            cert_path=cert_path,
    ) as client:
        return client.get_payment_info(prepay_id=prepay_id)


@commit
async def update_payment_info(
    app_id,
    api_key,
    cert_path,
    key_path,
    mchid,
    call_back_message: dict,
):
    """处理回调信息"""
    async with WxPayClient(
            app_id=app_id,
            mchid=mchid,
            key_path=key_path,
            api_key=api_key,
            cert_path=cert_path,
    ) as client:
        decrypted_msg = client.decrypt_callback_data(
            call_back_message['resource']['nonce'],
            call_back_message['resource']['ciphertext'],
            call_back_message['resource']['associated_data'],
        )
        decrypted_data = ujson.loads(decrypted_msg)

        out_trade_no = decrypted_data['out_trade_no']
        transaction_id = decrypted_data['transaction_id']
        success_time = decrypted_data['success_time']
        trade_type = decrypted_data['trade_type']
        trade_state = decrypted_data['trade_state']

        amount = decrypted_data['amount']
        total = amount['total']
        payer_total = amount['payer_total']
        currency = amount['currency']
        payer_currency = amount['payer_currency']

        order = await OrderModel.get_by_out_trade_no(out_trade_no)
        if order is None:
            logger.warning(f"未找到订单out_trade_no: {out_trade_no}")
            return

        user = await UserModel.create_by_wx_app_openid(decrypted_data['payer']['openid'])

        await PaymentModel.create(
            order_id=order.id,
            user_id=user.id,
            out_trade_no=out_trade_no,
            transaction_id=transaction_id,
            success_time=datetime.strptime(success_time[:19], "%Y-%m-%dT%H:%M:%S"),  # 2021-08-09T23:18:31+08:00
            trade_type=trade_type,
            trade_state=trade_state,  # SUCCESS 为成功
            total=total,
            payer_total=payer_total,
            currency=currency,
            payer_currency=payer_currency,
        )


async def get_payment_status(order_id: int = None, questionnaire_id: int = None) -> str:
    """
    :return: 支付成功 success；支付失败，fail； 正在支付 paying；
    :rtype: str
    """
    if order_id:
        if not (order := await OrderModel.get_by_id(order_id)):
            return "fail"

        return await order.get_paid_status()

    elif questionnaire_id:
        if not (q := await QuestionnaireModel.get_by_id(questionnaire_id)):
            return "fail"
        return await q.get_paid_status()

    else:
        return "fail"
