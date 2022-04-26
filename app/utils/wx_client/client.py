import base64
import random
import string
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse

import httpx
import ujson
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sanic.log import logger

from .api import get_session_token_api, order

POOL = string.ascii_uppercase + string.digits


def get_random_n(n: int) -> str:
    return "".join(random.choice(POOL) for _ in range(n))


class BaseClient:

    def __init__(self) -> None:
        self.session = httpx.AsyncClient()

    async def _send_request(self, api, method="get", *args, **kwargs) -> httpx.Response:
        t1 = time.time()
        logger.info(f"sending to {api}, payload is {args} and {kwargs}")
        res = await getattr(self.session, method)(api, *args, **kwargs)  # type: httpx.Response
        logger.info(
            f"sending request {api} success, cost {time.time() - t1} seconds, status {res.status_code} result is {res.content}"
        )
        return res

    async def close(self):
        await self.session.aclose()

    async def __aenter__(self):
        await self.session.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: None,
        exc_value: None,
        traceback: None,
    ) -> None:
        await self.session.__aexit__(exc_type, exc_value, traceback)


class WxMiniProgrammerClient(BaseClient):

    def __init__(self, app_id, app_secret) -> None:
        super().__init__()
        self.app_id = app_id,
        self.app_secret = app_secret

    async def get_session_code(self, code: str) -> dict:
        """
        获取session_code
        """
        res = await self._send_request(get_session_token_api,
                                       params=dict(
                                           appid=self.app_id,
                                           secret=self.app_secret,
                                           js_code=code,
                                           grant_type="authorization_code",
                                       ))
        return res.json()


class WxPayClient(BaseClient):

    def __init__(self,
                 app_id: str,
                 mchid: str,
                 key_path: str,
                 api_key: str,
                 cert_path: str,
                 serial_no: str = None) -> None:
        super().__init__()
        self.api_key = api_key.encode()
        self.app_id = app_id
        self.mchid = mchid
        self.key_path = key_path
        self.cert_path = cert_path

        with open(self.key_path, "r") as myfile:
            self.private_key = RSA.importKey(myfile.read())

        if not serial_no:
            from cryptography import x509
            cert = x509.load_pem_x509_certificate(open(self.cert_path, "rb").read())
            serial_no = f'{cert.serial_number:X}'

        self.serial_no = serial_no

    async def make_order(self, out_trade_no: str, price: int, openid: str, notify_url, description: str = ""):
        """微信支付下单

        :param out_trade_no: 订单号
        :type out_trade_no: str
        :param price: 价格，单位为分
        :type price: int
        :param openid: 用户的openid
        :type openid: str
        :param description: 订单描述
        :type description: str, optional
        """
        payload = dict(
            appid=self.app_id,
            mchid=self.mchid,
            description=description,
            notify_url=notify_url,
            out_trade_no=out_trade_no,
            time_expire=(datetime.now() + timedelta(minutes=5)).astimezone().isoformat(timespec="seconds"),
            amount=dict(total=price, currency="CNY"),
            payer=dict(openid=openid),
        )
        body = ujson.dumps(payload)
        header = self._get_auth_hearder("POST", order, body)
        res = await self._send_request(order, 'post', data=body, headers=header)
        return res.json()

    def _get_auth_hearder(self, method: str, url: str, payload: str = None) -> dict:
        """
        reference:
        https://wechatpay-api.gitbook.io/wechatpay-api-v3/qian-ming-zhi-nan-1/qian-ming-sheng-cheng#gou-zao-qian-ming-chuan

        加密的字符串由：构成
        HTTP请求方法\n
        URL\n
        请求时间戳\n
        请求随机串\n
        请求报文主体\n


        :param method: 请求方法
        :param url: 获取请求的绝对URL，并去除域名部分得到参与签名的URL。如果请求中有查询参数，URL末尾应附加有'?'和对应的查询字符串。
        :param payload: 需要上传的参数
        :rtype: dict[str, str]
                Authorization: WECHATPAY2-SHA256-RSA2048 mchid="",nonce_str="",signature="",timestamp="",serial_no=""
        """
        if payload is not None:
            content = payload
        else:
            content = ""
        print(content)
        parsed = urlparse(url)
        url_path = parsed.path + ("?" + parsed.query if parsed.query else "")

        nonce_str = get_random_n(32)
        timestamp = int(time.time())

        encrypt_str = f"{method.upper()}\n"\
                        f"{url_path}\n"\
                        f"{timestamp}\n"\
                        f"{nonce_str}\n"\
                        f"{content}\n"
        print(encrypt_str, end="")
        signature = self._sign(encrypt_str)

        return {
            "Authorization":
            f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mchid}"'
            f',nonce_str="{nonce_str}"'
            f',signature="{signature}"'
            f',timestamp="{timestamp}"'
            f',serial_no="{self.serial_no}"'
            "",
            "Content-Type":
            "application/json",
        }

    def get_payment_info(self, prepay_id: str) -> dict:
        """
        获取小程序支付信息

        https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_5_4.shtml

        :return dict, keys:
                appId,
                timeStamp,
                nonceStr,
                signType,
                paySign,
                package,
        """

        nonce_str = get_random_n(32)
        timestamp = int(time.time())
        package = f"prepay_id={prepay_id}"
        encrypt_str = f"{self.app_id}\n"\
                      f"{timestamp}\n"\
                      f"{nonce_str}\n"\
                      f"{package}\n"
        sign = self._sign(encrypt_str)
        return dict(
            appId=self.app_id,
            timeStamp=str(timestamp),
            nonceStr=nonce_str,
            signType="RSA",
            paySign=sign,
            package=package,
        )

    def _sign(self, sign_text: str) -> str:
        digest = SHA256.new()
        digest.update(sign_text.encode("utf8"))

        signer = PKCS1_v1_5.new(self.private_key)

        sig = signer.sign(digest)
        signature = base64.b64encode(sig).decode()
        return signature

    def decrypt_callback_data(self, nonce: str, ciphertext: str, associated_data: str) -> bytes:
        """用于解密微信的回调中的加密数据"""
        data = base64.b64decode(ciphertext)
        return self._decrypt_using_cryptography(nonce.encode(), data, associated_data.encode())

    def _decrypt_using_PyCryptodome(self, nonce, ciphertext, associated_data) -> bytes:
        """这个方法虽然可以传入 associated_data 但是不生效"""
        cipher = AES.new(self.api_key, AES.MODE_GCM, nonce).update(associated_data)
        return cipher.decrypt(ciphertext)

    def _decrypt_using_cryptography(self, nonce, ciphertext, associated_data) -> bytes:
        """wechat推荐的方式"""
        aesgcm = AESGCM(self.api_key)
        return aesgcm.decrypt(nonce, ciphertext, associated_data)

    def _verify_data(self, ):
        ...

    def _encrypt_important_data(self, data: bytes) -> bytes:
        cipher = PKCS1_OAEP.new(self.private_key)
        return cipher.encrypt(data)

    def _decrypt_important_data(self, data: bytes) -> bytes:
        cipher = PKCS1_OAEP.new(self.private_key)
        return cipher.decrypt(data)

    async def test(self):
        api = "https://api.mch.weixin.qq.com/v3/certificates"
        res = await self._send_request(api, headers=self._get_auth_hearder('get', api))
        print(res.json())
        return res


if __name__ == "__main__":
    import asyncio
    client = WxPayClient(
        app_id="wxcd7513c913588409",
        mchid="1611012534",
        key_path="app/certs/apiclient_key.pem",
        api_key="Y3gXxTe0BitmqsHWaJwLNHaTE7VOtlJh",
        cert_path="app/certs/apiclient_cert.pem",
    )
    pay_data = {
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
    # asyncio.run(client.test())
    print(
        client.decrypt_callback_data(
            pay_data['resource']['nonce'],
            pay_data['resource']['ciphertext'],
            pay_data['resource']['associated_data'],
        ), )
