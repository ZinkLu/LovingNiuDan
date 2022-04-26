from sanic import Blueprint

order_bp = Blueprint("order")

from . import urls
from . import views
