from nose import tools
import json
import mongoengine

from {{cookiecutter.project_slug}} import app

test_app = app.test_client()

mongoengine.connect('mongoenginetest', host='mongomock://localhost')


class BaseTest():
    # @classmethod
    # @tools.nottest
    # def test_login(cls, test_data=None):
    #     """
    #     测试登录是否成功，返回access_token
    #     """
    #     if test_data is None:
    #         test_data = user_data
    #     user = User(**test_data)
    #     user.password = util.md5(user.password)
    #     user.save()
    #     cls.user = user
    #     test_user = {'username': user.username,
    #                  'password': test_data.get('password', '')}
    #     data = json.dumps(test_user)

    #     response = test_app.post('/api/v1/login',
    #                              data=data,
    #                              content_type='application/json')

    #     json_resp = json.loads(response.data)
    #     cls.id = str(user.id)
    #     cls.token = f'JWT {json_resp["data"]["access_token"]}'

    # @classmethod
    # @tools.nottest
    # def clean_user(cls):
    #     cls.user.delete()

    # @tools.nottest
    # def test_api_jwt(self, api_url, api_method):
    #     """
    #     测试传入错误token和不传token时的情况
    #     """
    #     headers = {'Authorization': self.token + 'aaaa'}
    #     response = api_method(api_url)
    #     tools.assert_equals(response.status_code, 401)
    #     response = api_method(api_url, headers=headers)
    #     tools.assert_equals(response.status_code, 401)

    # @tools.nottest
    # def change_user_level(self, level=9):
    #     """
    #     测试修改用户权限
    #     """
    #     user = User.get_by_id(self.id)
    #     user.level = level
    #     user.save()

    @tools.nottest
    def validate_response(self, response, status_code=200):
        """
        验证返回结果是否正确，并返回 json_response body

        @param response:请求返回的 response
        @type response: http_response
        @param status_code: 请求结果状态码，默认为200
        @type status_code: int
        @return: json_response
        @rtype: dict
        """
        tools.assert_equals(response.status_code, status_code)
        return json.loads(response.data)
