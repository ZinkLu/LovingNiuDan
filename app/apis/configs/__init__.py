from sanic import Blueprint

config_bp = Blueprint("config")

from . import views
from . import urls
