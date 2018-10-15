from flask import request
from flask_restful import reqparse
from flask_jwt import jwt_required, JWTError

from geek_digest import app, rest_api, jwt
from geek_digest.common import util
from geek_digest.api.base import BaseAPI
from geek_digest.model.user import User
from geek_digest.service.user import rule_required, get_current_user
from geek_digest.service.user import save_new_user, update_user


@rest_api.route('/api/v1/login', endpoint='login')
class LoginAPI(BaseAPI):
    def post(self):
        """
        @api {post} /v1/login 登录
        @apiName login
        @apiGroup login
        @apiDescription 进行操作之前需要登录
        @apiVersion 1.0.0

        @apiParamExample {json} Request-Example:
        {
            "username":"admin",
            "password":"123456"
        }

        @apiSuccessExample {json} Success-Response:
        HTTP/1.1 200 OK
        {
            "data": {
                "access_token": "token string"
            }
        }

        @apiErrorExample {json} Error-Response:
        HTTP/1.1 401 ERROR
        {
            "data": {
                "msg": "Invalid credentials"
            }
        }
        """
        data = request.get_json()
        username = data.get(app.config.get('JWT_AUTH_USERNAME_KEY'), None)
        password = data.get(app.config.get('JWT_AUTH_PASSWORD_KEY'), None)
        criterion = [username, password, len(data) == 2]
        if not all(criterion):
            raise JWTError('Bad Request', 'Invalid credentials')

        identity = jwt.authentication_callback(
            User, username, util.md5(password))
        if identity:
            access_token = jwt.jwt_encode_callback(identity)
            return jwt.auth_response_callback(access_token, identity)
        else:
            raise JWTError('Bad Request', 'Invalid credentials')


@rest_api.route('/api/v1/user', endpoint='user')
@rest_api.route('/api/v1/user/<string:id>', endpoint='user_detail')
class UserAPI(BaseAPI):

    @jwt_required()
    def get(self, id=None):
        """
        @api {post} /v1/user 查询用户列表
        @apiName user_get
        @apiGroup user
        @apiDescription 查询用户
        @apiVersion 1.0.0

        @apiErrorExample {json} Error-Response:
        HTTP/1.1 500 ERROR
        {
            "data": {
                "msg": "Id is not found."
            }
        }
        """
        """
        @api {post} /v1/user/:id 查询用户详情
        @apiName user_get_detail
        @apiGroup user
        @apiDescription 查询用户
        @apiVersion 1.0.0

        @apiErrorExample {json} Error-Response:
        HTTP/1.1 500 ERROR
        {
            "data": {
                "msg": "Id is not found."
            }
        }
        """
        """
        @api {post} /v1/user/me 查询登录用户详情
        @apiName user_get_me
        @apiGroup user
        @apiDescription 查询用户
        @apiVersion 1.0.0

        @apiErrorExample {json} Error-Response:
        HTTP/1.1 500 ERROR
        {
            "data": {
                "msg": "Id is not found."
            }
        }
        """
        if id is None:
            parser = reqparse.RequestParser()
            parser.add_argument('page', type=int, default=1)
            parser.add_argument('page_size', type=int, default=20)
            args = parser.parse_args()

            data = util.paging(cls=User,
                               page=args.get('page'),
                               page_size=args.get('page_size'))

            return util.api_response(data=data)

        elif id == 'me':
            return util.api_response(data=self.me().api_response())
        else:
            return util.api_response(data=User.get_by_id(id).api_response())

    def me(self):
        return get_current_user()

    @jwt_required()
    @rule_required([9])
    def post(self):
        """
        @api {post} /v1/user 添加用户
        @apiName user_post
        @apiGroup user
        @apiDescription 添加用户
        @apiVersion 1.0.0

        @apiParamExample {json} Request-Example:
        {
            "username": "admin",
            "password": "0",
            "nickname": "Administrator",
            "name": "Administrator",
            "phone": "15562320082",
            "email": "wuwenhan@geekpark.net",
            "alive": true,
            "level": 9
        }

        @apiErrorExample {json} Error-Response:
            HTTP/1.1 500 ERROR
            {
                "msg": "User exists."
            }
        """
        data = dict(request.get_json())

        if User.get_by_username(data['username']):
            raise ValueError('该用户已存在')

        return util.api_response(data=save_new_user(data).api_response())

    @jwt_required()
    @rule_required()
    def put(self, id=None):
        """
        @api {post} /v1/user/:id 修改用户详情
        @apiName user_put
        @apiGroup user
        @apiDescription 修改用户
        @apiVersion 1.0.0

        @apiErrorExample {json} Error-Response:
        HTTP/1.1 400 ERROR
        {
            "data": {
                "msg": "Id not found"
            }
        }
        """
        if id is None:
            return util.api_error_response('Need user id.', 400)

        user = User.get_by_id(id)
        current_user = get_current_user()
        if user:
            if user.id != current_user.id and not current_user.is_admin:
                return util.api_error_response('Donnot have authority.')
            return util.api_response(
                update_user(request.get_json(), user).api_response())

        return util.api_error_response('Id not found', 400)
