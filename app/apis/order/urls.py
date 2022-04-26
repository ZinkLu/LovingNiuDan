from . import order_bp
from .views import OrderResource

order_bp.add_route(OrderResource.as_view(), '/order')
