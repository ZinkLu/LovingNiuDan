from sanic import Request
from sanic.exceptions import SanicException
from sanic.log import logger

from utils.exceptions.exception import ServiceException
from utils.responses.response_container import make_response
from . import app


@app.exception(SanicException)
async def sanic_exception(r, e: SanicException):
    return make_response(message=repr(e), status=e.status_code, code=e.status_code)


@app.exception(Exception)
async def base_exception(request: Request, e: Exception):
    logger.exception(e)
    return make_response(message=repr(e), status=500, code=500)


@app.exception(ServiceException)
async def service_exception(r, e: ServiceException):
    return make_response(message=e.message, status=e.status_code, code=e.status_code)
