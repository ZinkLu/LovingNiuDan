from sanic import Blueprint

common_bp = Blueprint("common")

from . import views
from . import urls
