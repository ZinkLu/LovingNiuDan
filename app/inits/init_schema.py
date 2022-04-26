from marshmallow.exceptions import ValidationError

from utils.responses.response_container import make_response
from . import app


@app.exception(ValidationError)
async def schema_error(request, error: ValidationError):
    return make_response(error.messages, message="wrong params", status=1, code=400)
