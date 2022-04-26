from sqlalchemy import Column, VARCHAR, SMALLINT, select

from sqlalchemy.dialects.postgresql import insert
from inits.init_db import session
from . import BaseModel


class UserModel(BaseModel):
    __tablename__ = "t_user"
    wx_openid = Column(VARCHAR(100), comment="用户的OpenID, 唯一, 关注公众号时自动生成", unique=True)  # 该字段适合另一张表
    wx_app_openid = Column(VARCHAR(100), comment="用户的小程序ID, 唯一, 使用小程序时自动生成", unique=True, nullable=True)
    union_id = Column(VARCHAR(100), comment="用户的UnionID, 同一用户，对同一个微信开放平台下的不同应用，unionid是相同的", unique=True, nullable=True)

    nickname = Column(VARCHAR(255), comment="用户昵称")
    mobile = Column(VARCHAR(32), comment="用户手机号")
    avatar_url = Column(VARCHAR(255), comment="用户头像")
    country = Column(VARCHAR(32), comment="国家")
    province = Column(VARCHAR(32), comment="省")
    city = Column(VARCHAR(32), comment="城市")
    gender = Column(SMALLINT, comment="性别, 0未知, 1男性, 2女性")
    language = Column(VARCHAR(32), comment="语言")

    @classmethod
    async def create_by_wx_app_openid(
        cls,
        wx_app_openid: str,
        **kwargs,
    ):
        """
        根据小程序OpenID创建用户, 如果有unionID传进来可能会出问题
        """
        statement = insert(cls.__table__).values(wx_app_openid=wx_app_openid).on_conflict_do_nothing()
        await session.execute(statement)
        result = await session.execute(select(UserModel).where(UserModel.wx_app_openid == wx_app_openid))
        user = result.scalar()
        await user.auto_setattr(**kwargs)
        return user
