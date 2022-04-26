from sanic import json
from sanic.response import BaseHTTPResponse


def make_response(data=None, message="success", status=0, code=200) -> BaseHTTPResponse:
    data = data or dict()
    payload = dict(data=data, message=message, status=status)
    return json(payload, code)
