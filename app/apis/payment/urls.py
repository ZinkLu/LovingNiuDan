from . import payment_bp
from .views import PaymentResource, PaymentCallback, PaymentCheck

payment_bp.add_route(PaymentResource.as_view(), '/payment')
payment_bp.add_route(PaymentCallback.as_view(), '/payment/callback')
payment_bp.add_route(PaymentCheck.as_view(), '/payment/check')
