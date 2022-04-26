from sanic import Blueprint

user_bp = Blueprint("user")

from . import views
from . import urls
