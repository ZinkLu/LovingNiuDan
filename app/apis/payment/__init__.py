from sanic import Blueprint

payment_bp = Blueprint("payment")

from . import urls
from . import views
