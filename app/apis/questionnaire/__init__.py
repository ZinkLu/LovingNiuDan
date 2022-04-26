from sanic import Blueprint

questionnaire_bp = Blueprint("questionnaire")

from . import urls
from . import views
