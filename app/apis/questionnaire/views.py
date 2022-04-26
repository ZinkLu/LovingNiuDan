import asyncio

from sanic import Request
from sanic.exceptions import InvalidUsage, NotFound
from sanic.views import HTTPMethodView

from inits.init_logger import logger
from schemas.questionnaire import QuestionnaireSchema
from services.questionnaire import create_questionnaire, get_printing_questionnaire_by_id, send_print_task
from services.user import get_or_create_user
from utils.mixin.wx_minin import EnsureWXCodeMixin
from utils.responses.response_container import make_response


class QuestionnaireResource(HTTPMethodView, EnsureWXCodeMixin):

    async def post(self, request: Request):
        app = request.app
        schema = QuestionnaireSchema()
        params = schema.load(request.json)

        logger.info("params is %s", params)
        openid = await self.ensure_wx_code(app.ctx.redis, params['code'])
        user = await get_or_create_user(openid)
        instance = await create_questionnaire(user_id=user.id, **params)

        json_data = schema.dump(instance)
        return make_response(json_data)

    async def get(self, request: Request):
        ...


class QuestionnairePrintResource(HTTPMethodView):

    async def post(self, request: Request):
        params = request.json
        app = request.app
        if not (q_id := params.get("questionnaire_id")):
            raise InvalidUsage("缺少 questionnaire_id")

        check = True
        if request.args.get("debug") == "true":
            logger.info("debug 模式，调过对问卷支付状态和打印状态的检查")
            check = False

        instance = await get_printing_questionnaire_by_id(q_id, check)

        if not instance:
            raise NotFound(f"未找到问卷{q_id}")

        res = await send_print_task(instance)
        logger.info(f"task published, {res} subscribed")

        logger.info("sleeping....")
        await asyncio.sleep(app.config.PRINT_SLEEP_TIME)
        return make_response(res)

    async def get(self, request: Request):
        ...
