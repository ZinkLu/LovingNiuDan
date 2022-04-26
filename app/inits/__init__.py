from sanic import Sanic, text
from importlib import import_module

app: Sanic


def create_app() -> Sanic:
    global app
    app = Sanic("lovingNiuDan")
    app.get("/ping")(lambda x: text("pong"))
    load_inits()
    return app


def load_inits():
    for module in [
            "init_configs",
            "init_schema",
            "init_exception",
            "init_db",
            "init_bp",
            "init_redis",
    ]:
        import_module(f"inits.{module}")
