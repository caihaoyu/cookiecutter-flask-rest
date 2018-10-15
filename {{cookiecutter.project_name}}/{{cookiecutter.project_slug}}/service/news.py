import datetime

import requests

from geek_digest.common.constant import RawArticleConstant
from geek_digest.model import RawArticle
from geek_digest.settings import CN_NEWS, EN_NEWS, SKR_API_KEY
from geek_digest.service.clause import ClauseArticle


clause = ClauseArticle()


class NewsService():
    def __init__(self, day=None, language=RawArticleConstant.LANGUAGE_CN):
        if day is None:
            day = datetime.datetime.today()
        self.day = day
        self.day_str = self.day.strftime('%Y%m%d')
        self.language = language
        self.api_url = CN_NEWS
        self.is_translated = True
        if language == RawArticleConstant.LANGUAGE_EN:
            self.api_url = EN_NEWS
            self.is_translated = False
            self.headers = {'apikey': SKR_API_KEY}
        self.params = {'day': self.day_str}
        self.punt_list = '。！？.!?'

    def __convert_news_list(self, news_list):
        """
        修改新闻列表里面的时间格式

        @param news_list: 新闻列表
        @type comment: list
        @return: 修改好的新闻列表
        @rtype: list
        """
        for news in news_list:
            news['date'] = news['date']['$date'] / 1000
        return news_list

    def get_news(self):
        """
        得到新闻

        @return: 接口返回的数据
        @rtype: dict
        """
        api_kwargs = {'url': self.api_url, 'params': self.params,
                      'headers': getattr(self, 'headers', None)}
        return requests.get(**api_kwargs).json()

    def __get_content(self, id):
        """
        通过详情接口得到正文

        @return: 正文数据
        @rtype: str
        """
        detail_url = f'{self.api_url}/{id}'
        api_kwargs = {'url': detail_url, 'timeout': 10,
                      'headers': getattr(self, 'headers', None)}
        response = requests.get(**api_kwargs).json()
        if response.get('data'):
            return response.get('data').get('content', '')
        return ''

    def save_news_to_db(self, news):
        """
        保存新闻到 RawArticle

        @param news: 接口返回的数据
        @type news: dict
        @return: none
        @rtype: none
        """
        for item in news.get('data', []):
            topic = item['topic']
            url = topic['url']
            article = RawArticle.objects(url=url).first()
            if not article:
                data = {f'{self.language}_title': topic['title'],
                        f'{self.language}_content': (
                            self.__get_content(item['_id'])),
                        f'{self.language}_summary': '',
                        'url': url,
                        'is_translated': self.is_translated,
                        'language': self.language,
                        'source': topic['source'],
                        'source_cn': topic['source_cn']
                        }
                topic_date = topic['date']['$date'] / 1000
                data['date'] = datetime.datetime.utcfromtimestamp(topic_date)
                article = RawArticle(**data)

            article.news_count = item['news_count']
            article.news = self.__convert_news_list(item['news'])
            article.updated = datetime.datetime.now()
            if article.language == RawArticleConstant.LANGUAGE_CN:
                article.cn_content, article.cn_summary = (
                    clause.sents_content(article.cn_content))
            article.save()

    def save_news(self):
        """
        读取接口保存到数据库

        @return: none
        @rtype: none
        """
        news = self.get_news()
        self.save_news_to_db(news)


def save_geeks_read():
    print('开始调度任务')
    service = NewsService()
    service.save_news()


def save_skr_news():
    print('开始调度任务')
    service = NewsService(language=RawArticleConstant.LANGUAGE_EN)
    service.save_news()


def delete_aritcles():
    day = datetime.date.today()
    RawArticle.objects(is_edited=False, added__lt=day).delete()
