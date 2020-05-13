from {{cookiecutter.project_slug}}.common import util


class BaseModel():

    def api_response(self):
        return util.api_response_generator(self)

    @classmethod
    def get_by_id(cls, id):
        try:
            item = cls.objects().get(id=id)
            return item
        except Exception as e:
            raise Exception('Id is not found.')

    def api_base_response(self):
        return util.api_response_generator(self)
