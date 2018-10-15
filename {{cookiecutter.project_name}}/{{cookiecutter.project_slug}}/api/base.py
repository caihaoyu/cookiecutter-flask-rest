import traceback
from werkzeug.exceptions import HTTPException

from flask_restful import Resource
from flask_restful.utils import cors
from flask_restful import Api
from flask_jwt import JWTError

from geek_digest import settings
from geek_digest.common import util


class BaseAPI(Resource):
    allow_headers = ['Content-Type',
                     'Access-Control-Allow-Headers',
                     'Authorization',
                     ' X-Requested-With', ]
    _pop_items = []

    def pop_data(self, data):
        for item in self._pop_items:
            data.pop(item, None)

    @cors.crossdomain(origin='*', headers=allow_headers)
    def options(self, id=None):
        return {'Allow': 'TRUE'}


class Service(Api):
    def handle_error(self, e):
        if isinstance(e, HTTPException):
            return super(Service, self).handle_error(e)
        elif isinstance(e, JWTError):
            data = {'msg': str(e.description)}
            return self.make_response(*util.api_response(data, e.status_code))
        else:
            if settings.PROJECT_ENV != 'test':
                traceback.print_exc()
            data = {'msg': str(e)}
            return self.make_response(*util.api_response(data, 500))
