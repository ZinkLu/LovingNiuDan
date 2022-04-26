from datetime import datetime

from sqlalchemy import INTEGER, Column, Enum, ForeignKey, TIMESTAMP

from utils.enums.status import BaseStatus

from . import BaseModel


class PrintTaskModel(BaseModel):
    __tablename__ = "t_print_task"

    questionnaire_id = Column(INTEGER, ForeignKey("t_questionnaire.id"), index=True)
    print_at = Column(TIMESTAMP, default=datetime.now)
    status = Column(Enum(BaseStatus), default=BaseStatus.processing)
