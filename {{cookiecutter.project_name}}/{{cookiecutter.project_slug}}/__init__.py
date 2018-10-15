import datetime
import types

from flask import Flask
from flask_jwt import JWT

from geek_digest import settings
from geek_digest.api.base import Service
from geek_digest.common import util
from geek_digest.model.user import authenticate, identity

app = Flask(__name__)

app.config['SECRET_KEY'] = settings.JWT_SECRET_KEY
app.config['JWT_AUTH_URL_RULE'] = None
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(
    days=settings.JWT_EXPIRATION_DELTA)
# app.config['JWT_AUTH_URL_OPTIONS'] = {'methods': ['POST', 'OPTIONS']}
jwt = JWT(app, authenticate, identity)


@jwt.jwt_payload_handler
def jwt_payload_handler(identity):
    iat = datetime.datetime.utcnow()
    exp = iat + app.config.get('JWT_EXPIRATION_DELTA')
    nbf = iat + app.config.get('JWT_NOT_BEFORE_DELTA')
    identity = getattr(identity, 'id', None) or identity['id']
    return {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': str(identity)}


@jwt.auth_response_handler
def auth_response_handler(access_token, identity):
    data = {'access_token': access_token.decode('utf-8')}
    return rest_api.make_response(*util.api_response(data=data))


def api_route(self, *args, **kwargs):
    def wrapper(cls):
        self.add_resource(cls, *args, **kwargs)
        return cls

    return wrapper


rest_api = Service(app)
rest_api.route = types.MethodType(api_route, rest_api)
