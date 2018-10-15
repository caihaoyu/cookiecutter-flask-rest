from datetime import datetime

import mongoengine

from geek_digest.model.base import BaseModel


class User(BaseModel, mongoengine.Document):
    username = mongoengine.StringField(required=True, unique=True)
    password = mongoengine.StringField(required=True)
    nickname = mongoengine.StringField(required=True, default='')
    name = mongoengine.StringField(required=True)
    phone = mongoengine.StringField(required=True, unique=True)
    email = mongoengine.EmailField(required=True, unique=True)
    added = mongoengine.DateTimeField(required=True, default=datetime.now)
    level = mongoengine.IntField(required=True, default=1)
    alive = mongoengine.BooleanField(required=True, default=False)

    meta = {
        'collection': 'user',
        'indexes': ['username', 'phone', 'email', 'added', 'level', 'alive'],
    }

    @classmethod
    def validate_password(cls, username, password):
        user = cls.get_by_username(username)
        if user and user.password.encode('utf-8') == password.encode('utf-8'):
            return user

    @classmethod
    def get_by_username(cls, username):
        return cls.objects(username=username).first()

    @property
    def is_admin(self):
        return self.level == 9

    @property
    def is_editor(self):
        return self.level == 2

    def api_base_response(self):
        return {'id': str(self.id), 'name': self.name}

    def me(self):
        return self.api_response()

    def api_response(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'nickname': self.nickname,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'alive': self.alive,
            'level': self.level
        }


def authenticate(user, username, password):
    user = User.validate_password(username, password)
    return user if user else None


def identity(payload):
    return User.objects.get(id=payload['identity'])
