from . import BaseModel

from sqlalchemy import Column, VARCHAR, DECIMAL, TIMESTAMP, ForeignKey


class PaymentModel(BaseModel):
    __tablename__ = "t_payment"

    order_id = Column(ForeignKey("t_order.id"), index=True)
    user_id = Column(ForeignKey("t_user.id"), index=True)
    out_trade_no = Column(VARCHAR(32), unique=True, comment="商户订单号")
    transaction_id = Column(VARCHAR(32), unique=True, comment="微信支付订单号", index=True)
    success_time = Column(TIMESTAMP(), comment="支付时间", index=True)
    trade_type = Column(VARCHAR(20),
                        comment="支付方式"
                        "JSAPI：公众号支付"
                        "NATIVE：扫码支付"
                        "APP：APP支付"
                        "MICROPAY：付款码支付"
                        "MWEB：H5支付"
                        "FACEPAY：刷脸支付")
    trade_state = Column(VARCHAR(20),
                         comment="支付状态 "
                         "SUCCESS：支付成功"
                         "REFUND：转入退款"
                         "NOTPAY：未支付"
                         "CLOSED：已关闭"
                         "REVOKED：已撤销（付款码支付）"
                         "USERPAYING：用户支付中（付款码支付）"
                         "PAYERROR：支付失败(其他原因，如银行返回失败")
    total = Column(DECIMAL(10, 2), comment="金额")
    payer_total = Column(DECIMAL(10, 2), comment="用户支付金额")
    currency = Column(VARCHAR(20), comment="币种")
    payer_currency = Column(VARCHAR(20), comment="用户支付币种")

    # 暂时不知道有啥用，冗余
    sp_openid = Column(VARCHAR(128), comment="用户服务标识")
    sub_openid = Column(VARCHAR(128), comment="用户子标识")
