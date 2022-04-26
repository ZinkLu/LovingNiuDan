from marshmallow import fields
from marshmallow.validate import OneOf
from marshmallow.validate import Length
from marshmallow_sqlalchemy import auto_field

from utils.enums.constellation import Constellation

from models.questionnaire import QuestionnaireModel
from . import BaseSchema


class QuestionnaireSchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        model = QuestionnaireModel

    code = fields.Str(required=True)
    self_introduction = auto_field(validate=Length(min=40, max=1024))
    constellation = fields.Function(
        serialize=lambda x: x.constellation and x.constellation.value or "",
        deserialize=lambda x: x,
        validate=OneOf(Constellation.__members__),
        missing=Constellation.noset,
    )
    picture_url = fields.Str(required=True)


def not_none_field(field_name, default="保密") -> fields.Function:
    return fields.Function(lambda x: getattr(x, field_name, None) or default)


class QuestionPrintSchema(BaseSchema):

    class Meta(BaseSchema.Meta):
        dateformat = "%Y年%m月%d日"
        # model = QuestionnaireModel
        fields = (
            'name',
            'gender',
            'birth_day',
            'height',
            'constellation',
            'profession',
            'education',
            'birth_place',
            'marriage',
            'hobbies',
            'contract',
            'self_introduction',
            'requirements',
            'picture_url'
        )

    EDU = {
        0: '保密',
        1: '小学',
        2: '初中',
        3: '中专',
        4: '高中',
        5: '大专',
        6: '本科',
        7: '研究生以上',
    }

    MARRIAGE = {
        0: '保密',
        1: '已婚',
        2: '未婚',
    }

    GENDER = {
        0: '保密',
        1: '男性',
        2: '女性',
    }

    name = not_none_field("name", default="")
    gender = fields.Function(serialize=lambda x: QuestionPrintSchema.GENDER.get(x.gender, "保密"))
    birth_day = fields.Date()
    height = not_none_field(field_name='height')
    constellation = fields.Function(serialize=lambda x: x.constellation and x.constellation.value or '保密')
    profession = not_none_field(field_name='profession')
    education = fields.Function(serialize=lambda x: QuestionPrintSchema.EDU.get(x.education, "保密"))
    birth_place = not_none_field(field_name='birth_place')
    marriage = fields.Function(serialize=lambda x: QuestionPrintSchema.MARRIAGE.get(x.marriage, "保密"))
    hobbies = not_none_field("hobbies", default="")
    contract = not_none_field("contract", default="")
    self_introduction = not_none_field("self_introduction", default="")
    requirements = not_none_field("requirements", default="")
    picture_url = not_none_field('picture_url', default='')
