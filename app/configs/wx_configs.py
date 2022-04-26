import os
from pathlib import Path

config_path = Path(__file__).absolute().parent

APP_ID = os.environ.get("APPID")
APP_SECRET = os.environ.get("APP_SECRET")
MERC_ID = os.environ.get("MERC_ID")
NOTIFY_URL = os.environ.get("NOTIFY_URL")
API_KEY = os.environ.get("API_KEY")
KEY_PATH = (config_path.parent / 'certs' / "apiclient_key.pem").as_posix()
CERT_PATH = (config_path.parent / 'certs' / "apiclient_cert.pem").as_posix()
