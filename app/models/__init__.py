from datetime import datetime
from typing import Optional

from sqlalchemy import BOOLEAN, INTEGER, Column, true, TIMESTAMP
from sqlalchemy.orm import declarative_base
from inits.init_db import session

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    active = Column(BOOLEAN, server_default=true(), nullable=False)
    create_time = Column(TIMESTAMP, default=datetime.now, comment="修改时间")
    last_update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now, comment="最近修改时间", index=True)

    async def auto_setattr(self, **kwargs):
        await session.refresh(self)
        for k, v in kwargs.items():
            if hasattr(self, k) and k != "id":
                setattr(self, k, v)

    @classmethod
    async def create(cls, **kawargs) -> "BaseModel":
        instance = cls(**{k: v for k, v in kawargs.items() if k in cls.__table__.columns})
        session.add_all([instance])
        await session.flush()
        await session.refresh(instance)
        return instance

    @classmethod
    async def get_by_id(cls, id: int) -> Optional["BaseModel"]:
        return await session.get(cls, id)


from .questionnaire import QuestionnaireModel
from .user import UserModel
from .print_task import PrintTaskModel
from .payment import PaymentModel
from .order import OrderModel
