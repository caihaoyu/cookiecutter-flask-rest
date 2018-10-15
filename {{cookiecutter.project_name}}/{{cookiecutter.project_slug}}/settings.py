import os

PROJECT_ENV = os.environ.get('PROJECT_ENV', 'test')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'geekpark-jwt')
JWT_EXPIRATION_DELTA = os.environ.get('JWT_EXPIRATION_DELTA', 6)

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '27017'))
DB_NAME = os.environ.get('DB_NAME', '{{cookiecutter.project_slug}}')


MIRROR_HOST = os.environ.get('MIRROR_HOST', 'http://data.geekpark.net')

MD5_SALT = os.environ.get('MD5_SALT', '')
