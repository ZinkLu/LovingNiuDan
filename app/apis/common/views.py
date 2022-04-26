import os
from uuid import uuid4
import base64

from sanic import Request
from sanic.exceptions import InvalidUsage
from sanic.views import HTTPMethodView

# from utils.mixin.wx_minin import EnsureWXCodeMixin
from utils.responses.response_container import make_response


class UploadResource(HTTPMethodView):

    async def post(self, request: Request):
        app = request.app  # type Sanic
        # if not request.files.get("file"):
        #     raise InvalidUsage("必须包含文件")
        # file = request.files["file"][0]

        # if 'image' not in file.type:
        #     raise InvalidUsage("上传必须是图片")
        if not request.json.get('data') or not request.json.get('file_name'):
            raise InvalidUsage("缺少图片")

        blob = request.json['data']
        file = base64.b64decode(blob)

        file_name = request.json['file_name']

        suffix = file_name.split('.')[-1]

        filename = f"{uuid4()}.{suffix}"

        static = app.config["STATIC_FOLDER"]

        with (static / filename).open('wb') as f:
            f.write(file)

        static_url = app.config['STATIC_URL']

        return make_response(os.path.join(static_url, filename))
