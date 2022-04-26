import ujson
from marshmallow import EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class BaseSchema(SQLAlchemyAutoSchema):

    class Meta:
        datetimeformat = "%Y-%m-%d %H:%M:%S"
        unknown = EXCLUDE
        render_module = ujson
