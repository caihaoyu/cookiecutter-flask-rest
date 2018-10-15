from threading import Timer
import json

from google.cloud import translate
import concurrent.futures
import requests
import html
import six

from geek_digest import settings
from geek_digest.model import RawArticle
from geek_digest.service.clause import ClauseArticle


clause = ClauseArticle()


def google_translate(text, target):
    """
    调用google翻译 翻译文本

    @param text: 需要翻译的文本
    @type text: str
    @param target: 翻译成的语言 如：en,zh-CN
    @type target: str
    @param is_content: 翻译的类型是否为正文
    @type is_content:boolean
    @return: 翻译结果
    @rtype: str
    """

    if text.strip() == '':
        return ''
    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(
        text, target_language=target)

    text = html.unescape(result['translatedText'])
    return text


def sogou_translate(text, target, from_lang='en'):
    """
    调用搜狗翻译 翻译文本

    @param text: 需要翻译的文本
    @type text: str
    @param target: 翻译成的语言 如：en,zh-CHS
    @type target: str
    @param is_content: 翻译的类型是否为正文
    @type is_content:boolean
    @return: 翻译结果
    @rtype: str
    """
    sogou_api_url = "http://snapshot.sogoucdn.com/engtranslate"
    data = {'from_lang': from_lang, 'to_lang': target,
            'trans_frag': [{'text': text}]}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
        url=sogou_api_url, headers=headers, data=json.dumps(data))
    json_response = response.json()
    if json_response.get('status', 0) < 0:
        raise Exception(json_response.get('error_string'))
    text = html.unescape(json_response['trans_result'][0]['trans_text'])
    return text


def translate_factory():
    """
    根据配置文件得到相应的翻译类型方法 搜狗或者google

    return: 相应的翻译方法
    rtype: method
    """
    translate_methods = {'sogou': sogou_translate, 'google': google_translate}
    return translate_methods[settings.TRANSLATE_FROM]


def translate_articles(article_list):
    """
    调用翻译接口翻译英文新闻，并保存

    @param article_list: 需要翻译的文本
    @type article_list: list of geek_digest.model.RawArticle
    @return: none
    @rtype: none
    """
    translate_method = translate_factory()
    for article in article_list:
        if not article.is_translated:
            try:
                article.cn_title = translate_method(text=article.en_title,
                                                    target='zh-CHS')
                article.cn_content = translate_method(text=article.en_content,
                                                      target='zh-CHS')
                article.is_translated = True
                article.en_content = clause.sents(article.en_content)
                article.cn_content, article.cn_summary = (
                    clause.sents_content(article.cn_content))

                article.save()
            except Exception as e:
                print(e)


def slice__(lst, slice_len=20):
    """
    切分数组变成一个二维数组

    example:
        - input: lst = [1,2,3,4,5],slice_len = 2
        - output: [[1,2],[3,4],[5]]

    @param lst: 需要切分的list
    @type lst: list
    @param slice_len: 每片长度,默认为20
    @type slice_len: int
    @return: 返回一个分好片的二维数组
    @rtype: list
    """
    lst = list(lst)
    if not lst:
        return []

    article_list = []
    for idx in range(len(lst) // slice_len + 1):
        start = idx * slice_len
        end = (idx + 1) * slice_len
        article_list.append(lst[start:end])

    return article_list


def translate_all():
    """
    使用多线程，翻译所有待翻译的文章
    """
    print('开始翻译')
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        articles = RawArticle.objects(is_translated__ne=True)
        print(len(articles))
        articles = slice__(articles, slice_len=20)
        executor.map(translate_articles, articles)
    print('结束翻译')
    t = Timer(600, translate_all)
    t.start()


if __name__ == '__main__':
    translate_all()
