import datetime
import re

import dateutil
from flask_restful import reqparse
from flask_jwt import jwt_required

from geek_digest import rest_api
from geek_digest.api.base import BaseAPI
from geek_digest.service.user import rule_required
from geek_digest.model.raw_article import RawArticle
from geek_digest.common import util
from geek_digest.common.constant import RawArticleConstant


parser = reqparse.RequestParser()


@rest_api.route('/api/v1/raw_article', endpoint='raw_article')
@rest_api.route('/api/v1/raw_article/<string:id>', endpoint='article_detail')
class RawArticleAPI(BaseAPI):
    @jwt_required()
    @rule_required()
    def get(self, id=None):
        """
        @api {get} /raw_article 获取原生文章列表
        @apiName raw_article_get
        @apiGroup raw_article
        @apiDescription 查询未编辑的文章列表
        @apiVersion 1.0.0

        @apiParam {Integer} [page_size] 每页条数
        @apiParam {Integer} [page] 页数
        @apiParam {List} [order_by] 排序字段
        @apiParam {String} [search] 搜索关键字
        @apiParam {String} [language] 原生文章语言
        @apiParam {String} [day] 搜索日期
        @apiParam {String} [is_cluster] 是否已聚类
        """
        """
        @api {get} /raw_article/:id 获取原生文章详情
        @apiName raw_article_get_detail
        @apiGroup raw_article
        @apiDescription 查询未编辑的文章列表
        @apiVersion 1.0.0

        @apiParam {Integer} [page_size] 每页条数
        @apiParam {Integer} [page] 页数
        @apiParam {List} [order_by] 排序字段
        @apiParam {String} [search] 搜索关键字
        @apiParam {String} [language] 原生文章语言
        @apiParam {String} [day] 搜索日期
        @apiParam {String} [is_cluster] 是否已聚类
        """
        if id:
            raw_article = RawArticle.get_by_id(id=id)
            return util.api_response(data=raw_article.api_response())
        else:
            parser.add_argument('page_size', type=int, default=20)
            parser.add_argument('page', type=int, default=1)
            parser.add_argument('order_by', type=str,
                                action='append', default=['-added'])
            parser.add_argument('search', type=str)
            parser.add_argument('language', type=str, default=None)
            parser.add_argument('day', type=str, default=None)
            parser.add_argument('is_cluster', type=str, default=None)
            args = parser.parse_args()
            page_size = args.get('page_size')
            page = args.get('page')
            order_by = args.get('order_by')

            query = {
                'is_edited': False,
                'is_translated': True,
            }

            if args.get('day'):
                day_str = args.get("day")
                time_range_query = self.__get_timerange(day_str)
                query = {**query, **time_range_query}
                if args.get('language') == RawArticleConstant.LANGUAGE_EN:
                    time_range_query = (self.__get_timerange(
                            day_str, language=RawArticleConstant.LANGUAGE_EN))
                    query = {**query, **time_range_query}

            if args.get('is_cluster') == 'true':
                query['news_count__gte'] = 3
            elif args.get('is_cluster') == 'false':
                query['news_count__lte'] = 2

            if args.get('language'):
                query['language'] = args.get('language')

            if args.get('search'):
                search = args.get('search')
                query_raw = {'$or': []}
                pattern = re.compile(search, re.IGNORECASE)
                query_raw['$or'].append({'en_title': {'$regex': pattern}})
                query_raw['$or'].append({'cn_title': {'$regex': pattern}})
                query['__raw__'] = query_raw

            result = util.paging(
                cls=RawArticle,
                page=page,
                query=query,
                page_size=page_size,
                order_by=order_by
            )

            return util.api_response(data=result)

    def __get_timerange(self, day_str, day_type=None, language='cn'):
        """
        按照时间进行查询，传added就按照新增时间

        @param day_str: 查询时间的字符串
        @type day_str: str
        @return: 按照时间查询的query
        @rtype: dict
        """
        if language == RawArticleConstant.LANGUAGE_EN:
            mintime = (dateutil.parser.parse(day_str) +
                       datetime.timedelta(hours=-3))
            maxtime = (dateutil.parser.parse(day_str) +
                       datetime.timedelta(hours=21))
            return {'date__gte': mintime, 'date__lte': maxtime}
        else:
            mintime = dateutil.parser.parse(day_str)
            maxtime = datetime.datetime.combine(mintime, datetime.time.max)
            return {'date__gte': mintime, 'date__lte': maxtime}
