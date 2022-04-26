from . import common_bp
from .views import UploadResource

common_bp.add_route(UploadResource.as_view(), "/upload")
