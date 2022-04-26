from . import login_bp
from .views import LoginResource

login_bp.add_route(LoginResource.as_view(), "/code")
