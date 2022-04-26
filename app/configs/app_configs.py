from pathlib import Path

ORDER_DESC = "打印服务"
ORDER_PRICE = 1  # 单位为分

PRINT_SLEEP_TIME = 1.3  # 单位为秒

STATIC_FOLDER = Path(__file__).parent.parent.parent / 'upload'  # static 静态文件
STATIC_URL = '/api/static'

STATIC_FOLDER.mkdir(exist_ok=True)
