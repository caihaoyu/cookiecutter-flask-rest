# from threading import Timer

import mongoengine
from flask_script import Manager
from flask_apidoc import ApiDoc
from flask_apidoc.commands import GenerateApiDoc
# from apscheduler.schedulers.background import BackgroundScheduler

from {{cookiecutter.project_slug}} import app, settings
from {{cookiecutter.project_slug}}.api import v1  # noqa: F401

mongoengine.connect(settings.DB_NAME,
                    host=settings.DB_HOST,
                    port=settings.DB_PORT)

ApiDoc(app=app,
       url_path='/api/docs',
       folder_path='.',
       dynamic_url=False)

manager = Manager(app)
manager.add_command('apidoc',
                    GenerateApiDoc(output_path='./{{cookiecutter.project_slug}}/static'))

if __name__ == '__main__':
    manager.run()
