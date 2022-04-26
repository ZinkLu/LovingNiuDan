import datetime
from typing import Optional

from sqlalchemy import DECIMAL, INTEGER, VARCHAR, Column, ForeignKey, and_, select
from sqlalchemy.sql.functions import count

from inits.init_logger import logger
from . import BaseModel, session
from .payment import PaymentModel


class OrderModel(BaseModel):
    __tablename__ = "t_order"

    questionnaire_id = Column(INTEGER, ForeignKey("t_questionnaire.id"), index=True)
    user_id = Column(INTEGER, ForeignKey("t_user.id"), index=True)
    price = Column(DECIMAL(10, 2), comment="订单金额")

    out_trade_no = Column(VARCHAR(32),
                          default=lambda: datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'),
                          unique=True,
                          index=True)
    wx_pay_no = Column(VARCHAR(64), index=True, unique=True)

    @classmethod
    async def get_by_out_trade_no(cls, out_trade_no) -> Optional['OrderModel']:
        stmt = select(cls).where(cls.out_trade_no == out_trade_no)
        res = await session.execute(stmt)
        return res.scalar()

    async def is_paid_success(self) -> bool:
        stmt = select(count(PaymentModel.id)).\
            select_from(PaymentModel).\
            where(
                and_(
                    PaymentModel.order_id == self.id,
                    PaymentModel.trade_state == "SUCCESS",
                ))

        res = await session.execute(stmt)
        total = res.scalar()
        logger.info("正在查询 %s 订单的成功支付记录 %s", self.id, total)
        return total > 0

    async def get_paid_status(self) -> str:
        """
        支付成功, success；      关联支付成功的payment
        支付失败，fail；        都不成功
        正在支付, paying；      没有关联支付单
        """
        stmt = select(PaymentModel).where(and_(PaymentModel.order_id == self.id))
        res = await session.execute(stmt)
        payments = list(res.scalars())
        if len(payments) == 0:
            return "paying"

        for payment in payments:
            if payment.trade_state == "SUCCESS":
                return "success"
        else:
            return "fail"
