from abc import ABCMeta, abstractmethod


class BaseModel(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def api_response(self):
        pass

    @classmethod
    def get_by_id(cls, id):
        try:
            item = cls.objects().get(id=id)
            return item
        except Exception as e:
            raise Exception('Id is not found.')

    @abstractmethod
    def api_base_response(self):
        pass
