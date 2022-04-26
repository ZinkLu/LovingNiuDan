from enum import Enum


class BaseStatus(Enum):
    success = "成功"
    fail = "失败"
    processing = "进行中"
