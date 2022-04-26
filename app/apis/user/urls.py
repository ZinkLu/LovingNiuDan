from . import user_bp
from .views import UserResource

user_bp.add_route(UserResource.as_view(), "/user")
