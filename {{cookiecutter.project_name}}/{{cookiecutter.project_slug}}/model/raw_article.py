from datetime import datetime

import mongoengine

from geek_digest.common.constant import RawArticleConstant
from geek_digest.model.base import BaseModel


class RawArticle(BaseModel, mongoengine.Document):
    cn_title = mongoengine.StringField(required=True, default='')
    cn_content = mongoengine.StringField(required=True, default='')
    cn_summary = mongoengine.StringField(required=True, default='')
    en_title = mongoengine.StringField(required=False, default='')
    en_content = mongoengine.StringField(required=False, default='')
    en_summary = mongoengine.StringField(required=False, default='')
    url = mongoengine.StringField(required=True, unique=True, default=None)
    source = mongoengine.StringField(required=True, default=None)
    source_cn = mongoengine.StringField(required=True, default=None)
    date = mongoengine.DateTimeField(required=True, default=datetime.now)
    added = mongoengine.DateTimeField(required=True, default=datetime.now)
    is_translated = mongoengine.BooleanField(required=True, default=False)
    is_edited = mongoengine.BooleanField(required=True, default=False)
    news = mongoengine.ListField()
    news_count = mongoengine.IntField(required=False, default=1)
    tag = mongoengine.ListField(required=False, default=[])
    language = mongoengine.StringField(
        required=False, default=RawArticleConstant.LANGUAGE_CN)

    meta = {'indexes': ['cn_title', 'en_title', 'url', 'source', 'source_cn',
                        'date', 'added', 'is_translated', 'is_edited',
                        'news_count', 'tag', 'language'],
            'strict': False
            }

    def api_response(self):
        data = self.api_base_response()
        data['cn_content'] = self.cn_content
        data['en_content'] = self.en_content
        return data

    def api_base_response(self):
        return {
            'id': str(self.id),
            'cn_title': self.cn_title,
            'en_title': self.en_title,
            'cn_summary': self.cn_summary,
            'en_summary': self.en_summary,
            'url': self.url,
            'source': self.source,
            'source_cn': self.source_cn,
            'added': self.added.timestamp(),
            'date': self.date.timestamp(),
            'news_count': self.news_count,
            'tag': self.tag,
            'language': self.language,
            'news': self.news
        }

    @classmethod
    def get_by_url(cls, url):
        """
        通过url查询数据库
        """
        return cls.objects(url=url).first()
