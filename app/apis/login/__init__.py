from sanic import Blueprint

login_bp = Blueprint("login")

from . import views
from . import urls
