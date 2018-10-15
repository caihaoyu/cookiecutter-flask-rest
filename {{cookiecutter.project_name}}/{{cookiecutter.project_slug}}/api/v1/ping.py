from geek_digest import rest_api
from geek_digest.common import util
from geek_digest.api.base import BaseAPI


@rest_api.route('/api/v1/ping', endpoint='ping')
class PingAPI(BaseAPI):

    def get(self):
        return util.api_response(data={
            'app_name': 'geek-digest',
            'app_version': '1.0',
            'revision': 'D49'
        })
