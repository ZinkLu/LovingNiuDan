from typing import Optional

import ujson

from configs.redis_configs import CHANNEL
from models.print_task import PrintTaskModel
from models.questionnaire import QuestionnaireModel
from schemas.questionnaire import QuestionPrintSchema
from utils.db_utils.commit import commit
from utils.exceptions.exception import ServiceException


@commit
async def create_questionnaire(**kwargs):
    instance = await QuestionnaireModel.create_with_serial(**kwargs)
    return instance


# @commit
async def send_print_task(questionnaire) -> int:
    questionnaire_id = questionnaire.id
    context = QuestionPrintSchema().dump(questionnaire)
    context['birth_day'] = context['birth_day'] or ''
    from inits.init_redis import redis_cli
    context = context or dict()
    await PrintTaskModel.create(questionnaire_id=questionnaire_id)
    return await redis_cli.publish(CHANNEL, ujson.dumps(context))


async def get_printing_questionnaire_by_id(q_id: int, check=True) -> Optional[QuestionnaireModel]:
    """获取打印的问卷，检查支付状态和打印状态"""
    instance = await QuestionnaireModel.get_by_id(q_id)
    if not instance:
        return

    if check:
        if await instance.is_printed():
            raise ServiceException("该问卷已经打印过了")

        if not await instance.is_paid_success():
            raise ServiceException("该问卷还没有进行支付")

    return instance
