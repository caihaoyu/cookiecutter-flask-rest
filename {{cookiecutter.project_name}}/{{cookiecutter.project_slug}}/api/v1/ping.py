from {{cookiecutter.project_slug}} import rest_api
from {{cookiecutter.project_slug}}.common import util
from {{cookiecutter.project_slug}}.api.base import BaseAPI


@rest_api.route('/api/v1/ping', endpoint='ping')
class PingAPI(BaseAPI):

    def get(self):
        return util.api_response(data={
            'app_name': '{{cookiecutter.project_name}}',
            'app_version': '1.0'
        })
