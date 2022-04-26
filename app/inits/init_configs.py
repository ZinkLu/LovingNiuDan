from . import app

from configs import (db_configs, wx_configs, app_configs, redis_configs)

app.update_config(db_configs)
app.update_config(wx_configs)
app.update_config(app_configs)
app.update_config(redis_configs)

app_configs = app.config
app.static(app.config['STATIC_URL'], app.config['STATIC_FOLDER'])
