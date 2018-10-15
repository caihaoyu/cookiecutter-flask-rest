import datetime
from functools import wraps

from flask import _request_ctx_stack

from geek_digest.common import util
from geek_digest.model.user import User


def save_new_user(data):
    """
    根据接口传入数据，保存用户

    @param data: 接口传入的数据
    @type data: dict
    @return: 保存成功的用户
    @rtype: User
    """
    data['username'] = data['username'].strip()
    data['nickname'] = data['nickname'].strip()
    data['name'] = data['name'].strip()
    data['phone'] = data['phone'].strip()
    data['password'] = util.md5(data['password'].strip())
    data['email'] = data['email'].strip()
    data['added'] = datetime.datetime.now()

    user = User(**data).save()

    return user


def update_user(data, user):
    """
    根据接口传入数据，更新用户

    @param data: 接口传入的数据
    @type data: dict
    @param user: 需要更新的目标用户
    @type user: User
    @return: 更新好的用户
    @rtype: User
    """
    if data.get('password', None):
        user.password = util.md5(data['password'].strip())
    if user.level == 9:
        user.username = data.get('username', user.username).strip()
        user.level = data.get('level', user.level)
        user.alive = data.get('alive', user.alive)
    user.nickname = data.get('nickname', user.nickname).strip()
    user.name = data.get('name', user.name).strip()
    user.phone = data.get('phone', user.phone).strip()
    user.email = data.get('email', user.email).strip()

    return user.save()


def rule_required(level=None):
    """
    权限装饰器，只有当前用户属于传入的权限组内，才能进行操作，否则会报错

    @param level: 权限组
    @type level: list
    """
    if level is None:
        # 2 部门主管 9 管理员
        level = [2, 9]

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user = get_current_user()
            if user.level not in level:
                raise Exception("user don't has authority")
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def get_current_user():
    """
    得到当前用户
    """
    return _request_ctx_stack.top.current_identity
