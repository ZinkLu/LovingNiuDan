from uuid import uuid4

from sqlalchemy import DATE, INTEGER, SMALLINT, VARCHAR, Column, Enum, ForeignKey, and_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.functions import count

from inits.init_logger import logger
from models.order import OrderModel
from models.payment import PaymentModel
from models.print_task import PrintTaskModel
from utils.enums.constellation import Constellation
from utils.enums.status import BaseStatus
from . import BaseModel, session


class QuestionnaireModel(BaseModel):
    __tablename__ = "t_questionnaire"

    user_id = Column(INTEGER(), ForeignKey("t_user.id"))
    serial = Column(VARCHAR(50), unique=True, comment="编号", default=lambda: str(uuid4()))

    name = Column(VARCHAR(50), comment="姓名", default="")
    gender = Column(SMALLINT(), comment="0保密, 1男性, 2女性", default=0)
    birth_day = Column(DATE(), comment="生日")
    height = Column(SMALLINT(), comment="身高，单位厘米", default=0)
    constellation = Column(Enum(Constellation), comment="星座", default="")
    profession = Column(VARCHAR(100), comment="职业", default='')
    education = Column(SMALLINT(), comment="学历, 0保密, 1小学, 2初中, 3中专, 4高中, 5大专, 6本科, 7研究生以上", default=0)
    birth_place = Column(VARCHAR(50), comment="出生地", default='')
    marriage = Column(SMALLINT(), comment="婚姻状况, 0保密, 1已婚, 2未婚", default=0)
    hobbies = Column(VARCHAR(255), comment="兴趣爱好", default='')
    contract = Column(VARCHAR(255), comment="联系方式", default='')
    self_introduction = Column(VARCHAR(1024), comment="个人介绍", default='')
    requirements = Column(VARCHAR(1024), comment="需求", default='')
    picture_url = Column(VARCHAR(1024), comment="图片链接")

    @classmethod
    async def create_with_serial(cls, serial=None, **kwargs) -> "QuestionnaireModel":
        if not serial:
            return await cls.create(**kwargs)
        statement = insert(cls.__table__).values(serial=serial).on_conflict_do_nothing()
        await session.execute(statement)
        result = await session.execute(select(QuestionnaireModel).where(QuestionnaireModel.serial == serial))
        questionnaire = result.scalar()
        await questionnaire.auto_setattr(**kwargs)
        return questionnaire

    async def is_paid_success(self) -> bool:
        stmt = select(OrderModel).\
            where(OrderModel.questionnaire_id == self.id).\
            order_by(OrderModel.last_update_time.desc())
        res = await session.execute(stmt)
        for order in res.scalars():
            if await order.is_paid_success():
                return True
        return False

    async def get_paid_status(self) -> str:
        """
        支付成功, success；     关联支付成功的payment
        支付失败，fail；        都不成功
        正在支付, paying；      没有关联支付单
        """
        stmt = select(PaymentModel).\
            join(OrderModel, OrderModel.id == PaymentModel.order_id).\
            join(QuestionnaireModel, QuestionnaireModel.id == OrderModel.questionnaire_id)

        res = await session.execute(stmt)
        payments = list(res.scalars())

        if len(payments) == 0:
            return "paying"

        for payment in payments:
            if payment.trade_state == "SUCCESS":
                return "success"
        else:
            return "fail"

    async def is_printed(self) -> bool:
        stmt = select(count(PrintTaskModel.id)).\
            select_from(PrintTaskModel).\
            where(and_(PrintTaskModel.questionnaire_id == self.id,
                       PrintTaskModel.status == BaseStatus.success))

        res = await session.execute(stmt)
        total = res.scalar()
        logger.info("正在查询问卷号 %s 的打印次数 %s", self.id, total)
        return total > 0
