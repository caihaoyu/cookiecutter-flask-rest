import time
from datetime import datetime

import mongoengine

from geek_digest import settings
from geek_digest.model.base import BaseModel
from geek_digest.common.constant import (
    EditedAriticleConstant as article_constant)

aritcle_from_choices = list(article_constant.ARTICLE_FROM.values())


class EditedArticle(BaseModel, mongoengine.Document):
    cn_title = mongoengine.StringField(required=True, default='')
    cn_content = mongoengine.StringField(required=True, default='')
    cn_summary = mongoengine.StringField(required=True, default='')
    en_title = mongoengine.StringField(required=False, default='')
    en_content = mongoengine.StringField(required=False, default='')
    en_summary = mongoengine.StringField(required=False, default='')
    state = mongoengine.StringField(required=True, default=datetime.now,
                                    choices=article_constant.ARTICLE_STATE)
    tag = mongoengine.ListField(required=False, default=[])
    url = mongoengine.URLField(required=True, unique=True, default=None)
    source = mongoengine.StringField(required=True, default=None)
    source_cn = mongoengine.StringField(required=True, default=None)
    published = mongoengine.DateTimeField(required=True, default=datetime.now)
    added = mongoengine.DateTimeField(required=True, default=datetime.now)
    updated = mongoengine.DateTimeField(required=True, default=datetime.now)
    date = mongoengine.DateTimeField(required=True, default=datetime.now)
    raw_article = mongoengine.ReferenceField('RawArticle', required=False,
                                             default=None)
    article_from = mongoengine.IntField(require=False, default=0,
                                        choices=aritcle_from_choices)
    news = mongoengine.ListField()
    news_count = mongoengine.IntField(required=False, default=1)
    creator = mongoengine.ReferenceField('User', required=True, default=None)
    meta = {'indexes': ['cn_title', 'en_title', 'state', 'date',
                        'raw_article', 'tag', 'url', 'source',
                        'source_cn', 'published', 'added', 'news_count',
                        'article_from', 'creator', 'updated']}

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
            'en_summary': self.en_summary,
            'cn_summary': self.cn_summary,
            'url': self.url,
            'source': self.source,
            'source_cn': self.source_cn,
            'published': self.published.timestamp(),
            'added': self.added.timestamp(),
            'updated': self.added.timestamp(),
            'date': self.date.timestamp(),
            'article_from': self.article_from,
            'news_count': self.news_count,
            'state': self.state,
            'tag': self.tag,
            'raw_article': (str(self.raw_article.id)
                            if self.raw_article else {}),
            'creator': self.creator.api_response(),
            'news': self.news
        }

    def api_holoread_response(self):
        return {
            '_id': str(self.id),
            'accesses': [],
            'createdAt': int(self.added.timestamp()),
            'edited_title': self.cn_title,
            'hot': False,
            'icon': settings.ICON_URL.format(source=self.source),
            'is_cn': True,
            'like': False,
            'likes': [],
            'published': (time.strftime('%Y-%m-%dT%H:%M:%S',
                          time.gmtime(self.published.timestamp()))
                          + '+08:00'),
            'source': self.source,
            'state': "normal",
            'summary': self.cn_summary,
            'updatedAt': int(self.published.timestamp()),
            'url': self.url
        }
