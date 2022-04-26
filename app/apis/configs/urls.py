from . import config_bp
from .views import ConfigResource

config_bp.add_route(ConfigResource.as_view(), "/config")
