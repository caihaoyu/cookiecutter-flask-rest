import datetime
import time
import re

import dateutil
from flask import request
from flask_restful import reqparse
from flask_jwt import jwt_required

from geek_digest import rest_api
from geek_digest.api.base import BaseAPI
from geek_digest.common import util
from geek_digest.common.constant import EditedAriticleConstant
from geek_digest.model import EditedArticle, RawArticle
from geek_digest.service.user import rule_required, get_current_user


parser = reqparse.RequestParser()


def get_page(query=None, page=1, page_size=20, order_by=None):
    """
    得到分页数据

    @param cls: 分页的model
    @type: mongoengine.Document
    @param field: 需要分页的字段名
    @type field: str
    @param query: 查询语句
    @type query: dict
    @param page: 当前页面
    @type page: int
    @param page_size: 每页条数
    @type page_size: int
    @param order_by: 排序语句 如: ['-added','-name']
    @type order_by: list of str
    @return: 分页结果
    @rtype: dict
    """
    if query is None:
        query = {}
    if order_by is None:
        order_by = []

    result = util.paging(
        cls=EditedArticle,
        page=page,
        query=query,
        page_size=page_size,
        order_by=order_by
    )
    return util.api_response(data=result)


def search_function(search):
    query_raw = {'$or': []}
    pattern = re.compile(search, re.IGNORECASE)
    query_raw['$or'].append({'en_title': {'$regex': pattern}})
    query_raw['$or'].append({'cn_title': {'$regex': pattern}})
    return query_raw


@rest_api.route('/api/v1/news', endpoint='news_list')
@rest_api.route('/api/v1/news/<string:id>', endpoint='news_detail')
class NewsAPI(BaseAPI):

    def detail(self, id):
        edited_article = EditedArticle.get_by_id(id)
        if edited_article.state != EditedAriticleConstant.STATE_PUBLISHED:
            return util.api_error_response('forbidden.', 403)
        return util.api_response(data=edited_article.api_response())

    def get(self, id=None):
        """
        @api {get} /news 获取新闻列表
        @apiName news
        @apiGroup news
        @apiDescription 按照各种条件查询新闻列表
        @apiVersion 1.0.0

        @apiParam {Integer} [page_size] 每页条数
        @apiParam {Integer} [page] 页数
        @apiParam {String} [day] 查询日期
        @apiParam {String} [added] 增加查询日期范围
        @apiParam {String} [order_by] 发布时间或排序时间
        """
        """
        @api {get} /news/:id 获取新闻详情
        @apiName news_detail
        @apiGroup news
        @apiDescription 按照各种条件查询新闻列表
        @apiVersion 1.0.0

        @apiParam {Integer} [page_size] 每页条数
        @apiParam {Integer} [page] 页数
        @apiParam {String} [day] 查询日期
        @apiParam {String} [search] 搜索关键字
        @apiParam {String} [added] 增加查询日期范围
        @apiParam {String} [order_by] 发布时间或排序时间
        """
        if id:
            return self.detail(id)
        else:
            parser.add_argument('page_size', type=int, default=20)
            parser.add_argument('page', type=int, default=1)
            parser.add_argument('day', type=str)
            parser.add_argument('search', type=str)
            parser.add_argument('added', type=str)
            parser.add_argument('order_by', type=str,
                                action='append', default=['-published'])

            args = parser.parse_args()

            query = {}

            if args.get('day'):
                day_type = None
                if args.get('added'):
                    day_type = 'added'
                day = datetime.datetime.strptime(args.get('day'), "%Y%m%d")
                query = self.__get_timerange(str(day), day_type)

            if args.get('search'):
                search = args['search']
                query['__raw__'] = search_function(search)

            order_by = args.get('order_by')
            page_size = args.get('page_size')
            page = args.get('page')

            query['state'] = EditedAriticleConstant.STATE_PUBLISHED

            return get_page(query, page, page_size, order_by)

    def __get_timerange(self, day_str, day_type=None):
        """
        按照时间进行查询，传added就按照新增时间

        @param day_str: 查询时间的字符串
        @type day_str: str
        @param day_type: 新增的时间，默认为None
        @type day_type: str
        @return: 所有符合时间条件的文章
        @rtype: dict
        """
        mintime = dateutil.parser.parse(day_str)
        maxtime = datetime.datetime.combine(mintime, datetime.time.max)
        if day_type == 'added':
            return {'added__gte': mintime, 'added__lte': maxtime}
        return {'published__gte': mintime, 'published__lte': maxtime}


@rest_api.route('/api/v1/articles', endpoint='articles')
class HoloreadArticleAPI(BaseAPI):
    def get(self):
        """
        @api {get} /articles 获取文章列表
        @apiName articles
        @apiGroup articles
        @apiDescription 适配旧接口查询published文章列表
        @apiVersion 1.0.0

        @apiParam {Integer} [last] 时间戳
        @apiParam {Integer} [count] 显示的新闻条数
        """
        parser.add_argument('last', type=int,
                            default=int(time.time()) - 24 * 60 * 60)
        parser.add_argument('count', type=int, default=1000)
        args = parser.parse_args()
        last = args.get('last')
        count = args.get('count')
        order_by = ['published']
        query = {
            'state': EditedAriticleConstant.STATE_PUBLISHED,
            'published__gte': datetime.datetime.fromtimestamp(last)
        }
        article_data = (EditedArticle.objects(**query).
                        order_by(*order_by).limit(count))

        article_list = [
            art.api_holoread_response()
            for art in article_data
        ]
        return util.api_response(data=article_list)


@rest_api.route('/api/v1/edited', endpoint='edited')
@rest_api.route('/api/v1/edited/<string:id>', endpoint='edited_detail')
class EditedArticleAPI(BaseAPI):
    _pop_items = ['added', 'date', 'article_from',
                  'creator', 'published', 'updated']

    @jwt_required()
    @rule_required()
    def get(self, id=None):
        """
        @api {get} /edited 获取文章列表
        @apiName edited_article_get
        @apiGroup edited_article
        @apiDescription 按照各种条件查询文章列表
        @apiVersion 1.0.0

        @apiParam {String} [state] 待处理、已处理等状态
        @apiParam {Integer} [page_size] 每页条数
        @apiParam {List} [order_by] 爬取时间或排序时间
        @apiParam {Integer} [page] 页数
        """
        """
        @api {get} /articles/:id 获取文章详情
        @apiName edited_article_get_detail
        @apiGroup edited_article
        @apiDescription 按照各种条件查询文章列表
        @apiVersion 1.0.0

        @apiParam {String} [state] 待处理、已处理等状态
        @apiParam {Integer} [page_size] 每页条数
        @apiParam {List} [order_by] 爬取时间或排序时间
        @apiParam {String} [search] 搜索关键字
        @apiParam {Integer} [page] 页数
        """
        if id:
            edited_article = EditedArticle.get_by_id(id=id)
            return util.api_response(data=edited_article.api_response())
        else:
            parser.add_argument('state', type=str, default='all')
            parser.add_argument('page_size', type=int, default=20)
            parser.add_argument('order_by', type=str,
                                action='append', default=['-updated'])
            parser.add_argument('search', type=str)
            parser.add_argument('page', type=int, default=1)
            args = parser.parse_args()
            page_size = args.get('page_size')
            page = args.get('page')
            state = args.get('state')
            order_by = args.get('order_by')
            query = {}

            if args.get('search'):
                search = args['search']
                query['__raw__'] = search_function(search)

            if state != 'all':
                query['state'] = state
            return get_page(query, page, page_size, order_by)

    @jwt_required()
    @rule_required()
    def post(self):
        """
        @api {post} /edited 新增文章
        @apiName edited_article_post
        @apiGroup edited_article
        @apiDescription 保存文章到edited_article数据库
        @apiVersion 1.0.0

        @apiParam {String} [cn_title] 编辑后标题
        @apiParam {String} [cn_content] 编辑后正文
        @apiParam {String} [cn_summary] 摘要
        @apiParam {String} [en_title] 英文标题
        @apiParam {String} [en_content] 英文正文
        @apiParam {String} [en_summary] 英文摘要
        @apiParam {String} [url] 原始链接
        @apiParam {String} [source] 来源
        @apiParam {String} [state] 编辑状态
        @apiParam {String} [published] 发布时间
        """
        data = request.get_json(force=True)
        self.pop_data(data)
        if data.get('state') == EditedAriticleConstant.STATE_PUBLISHED:
            data['published'] = datetime.datetime.now()

        data['creator'] = get_current_user()

        if data.get('raw_article'):
            raw_article = RawArticle.get_by_id(data.get('raw_article'))
            data['raw_article'] = raw_article
            edited_article = EditedArticle(**data).save()
            edited_article.raw_article.is_edited = True
            edited_article.raw_article.save()
        else:
            data['article_from'] = 1
            edited_article = EditedArticle(**data)
            edited_article.save()
        if edited_article:
            return util.api_response(edited_article.api_response())
        else:
            raise ValueError('save failure')

    @jwt_required()
    @rule_required()
    def put(self, id=None):
        """
        @api {put} /edited 修改文章
        @apiName edited_article_put
        @apiGroup edited_article
        @apiDescription 修改edited_article的文章
        @apiVersion 1.0.0

        @apiParam {String} [cn_title] 编辑后标题
        @apiParam {String} [cn_content] 编辑后正文
        @apiParam {String} [cn_summary] 摘要
        @apiParam {String} [en_title] 英文标题
        @apiParam {String} [en_content] 英文正文
        @apiParam {String} [en_summary] 英文摘要
        @apiParam {String} [url] 原始链接
        @apiParam {String} [source] 来源
        @apiParam {String} [state] 编辑状态
        @apiParam {String} [published] 发布时间
        @apiParam {String} [updated] 更新时间
        """
        data = request.get_json(force=True)
        self.pop_data(data)
        if id is None:
            return util.api_error_response(
                'ID cannot be None.', status_code=400)
        if data.get('state') == EditedAriticleConstant.STATE_PUBLISHED:
            data['published'] = datetime.datetime.now()
        if data.get('raw_article'):
            raw_article = RawArticle.get_by_id(data.get('raw_article'))
            data['raw_article'] = raw_article
        edited_article = EditedArticle.get_by_id(id=id)
        if edited_article:
            data['date'] = datetime.datetime.now()
            data['updated'] = datetime.datetime.now()
            edited_article.update(**data)
            edited_article.reload()
            return util.api_response(data=edited_article.api_response())
        else:
            raise ValueError('edited_article not found')
