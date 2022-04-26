from sanic.blueprint_group import BlueprintGroup

from .configs import config_bp
from .login import login_bp
from .order import order_bp
from .payment import payment_bp
from .questionnaire import questionnaire_bp
from .user import user_bp
from .common import common_bp

group = BlueprintGroup(url_prefix="/api")

group.append(login_bp)
group.append(user_bp)
group.append(questionnaire_bp)
group.append(payment_bp)
group.append(order_bp)
group.append(config_bp)
group.append(common_bp)
