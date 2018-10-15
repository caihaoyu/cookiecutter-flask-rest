import hashlib

import mongoengine

from geek_digest import settings


def paging(cls=None, field=None, page=None, page_size=None, order_by=None,
           query=None):
    """
    分页函数 支持按照字段分页

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
    if page is None:
        page = 1
    if page_size is None:
        page_size = 10
    if order_by is None:
        order_by = []
    if not isinstance(cls(), mongoengine.Document):
        raise 'Class is not extend mongoengine.Document'

    def get_limit(count, page, page_size):
        if page <= 0:
            page = 1
        page_sum = int((count - 1) / page_size + 1)
        start = (page - 1) * page_size
        has_previous = True if page > 1 else False
        has_next = True if page < page_sum else False
        return {'start': start, 'page_sum': page_sum,
                'has_next': has_next, 'has_previous': has_previous,
                'count': count}

    if field:
        pipeline = [{'$project': {'count': {'$size': '$' + field}}}]
        count = list(cls.objects(**query).aggregate(*pipeline))[0]['count']
        results = get_limit(count, page, page_size)
        fields_query = {f'slice__{field}': [results['start'], page_size]}
        list_ = cls.objects(**query).fields(**fields_query).order_by(*order_by)
        results['list'] = list_[0][field]
    else:
        count = cls.objects(**query).count()
        results = get_limit(count, page, page_size)
        qery_set = cls.objects(**query).order_by(*order_by)
        list_ = qery_set.skip(results['start']).limit(page_size)
        # results['list'] = json.loads(list_.to_json())
        results['list'] = list(map(lambda a: a.api_base_response(), list_))

    results['current_page'] = page
    results.pop('start', None)
    return results


def api_response(data=None, status_code=200):
    """
    生成api标准response

    @param data: api返回的数据，只要能够JSON serializable都是可以的。比如:
        list,str,dict,int,float,bool,None
    @type data: object of JSON serializable
    @param status_code: Http 状态码
    @type status_code: int
    @return: response body, status code, headers
    @rtype: dict,int,dict
    """
    if data is None:
        data = {}
    return {'data': data}, status_code, {'Access-Control-Allow-Origin': '*'}


def api_error_response(msg, status_code=500):
    """
    生成api发生错误时的response

    @param msg: 错误信息
    @type msg: str
    @return: response body, status code, headers
    @rtype: dict, int, dict
    """
    return {'msg': msg}, status_code, {'Access-Control-Allow-Origin': '*'}


def sha512_hash(fn):
    """
    使用sha512算法对md5的返回值加密装饰器
    """
    def wrapper(*args, **kwargs):
        password = fn(*args, **kwargs)
        sha512 = hashlib.sha512()
        sha512.update(password.encode('utf-8'))
        res = sha512.hexdigest()
        return res
    return wrapper


@sha512_hash
def md5(text):
    """
    md5加密

    @param text: 需要加密的文本
    @type text: str
    @return: 加密好的文本
    @rtype: str
    """
    text += settings.MD5_SALT
    h = hashlib.md5()
    h.update(text.encode())
    return h.hexdigest()
