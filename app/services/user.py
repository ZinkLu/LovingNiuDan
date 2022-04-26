from utils.db_utils.commit import commit
from utils.wx_biz_data_crypt import WXBizDataCrypt
from utils.wx_client.client import WxMiniProgrammerClient

from models import UserModel


async def get_session_token(app_id: str, app_secret: str, code: str) -> dict:
    """
    获取 session_token
    https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html
    """
    async with WxMiniProgrammerClient(app_id, app_secret) as client:
        res = await client.get_session_code(code)
        return res


@commit
async def get_or_create_user(wx_app_openid, **kwargs) -> UserModel:
    return await UserModel.create_by_wx_app_openid(wx_app_openid, **kwargs)


@commit
async def create_user_by_encrypted_data(
    app_id: str,
    session_key: str,
    encrypted_data: str,
    iv: str,
):
    """似乎加密的信息中不再包含openid等信息，因此该方法暂时弃用
    """
    return _decrypt_data(app_id, session_key, encrypted_data, iv)


def _decrypt_data(
    app_id,
    session_key,
    encrypted_data,
    iv,
) -> dict:
    """解密加密信息，代码来源于微信官方demo
    """
    crypter = WXBizDataCrypt(appId=app_id, sessionKey=session_key)
    return crypter.decrypt(encryptedData=encrypted_data, iv=iv)
