class RawArticleConstant(object):
    LANGUAGE_CN = 'cn'
    LANGUAGE_EN = 'en'


class EditedAriticleConstant(object):
    ARTICLE_FROM = {
        'RAW_ARTICLE': 0,
        'ADD_EDITED_ARTICLE': 1
    }
    STATE_EDITED = 'edited'
    STATE_PENDING = 'pending'
    STATE_DELETED = 'deleted'
    STATE_PUBLISHED = 'published'
    ARTICLE_STATE = [STATE_DELETED, STATE_EDITED,
                     STATE_PENDING, STATE_PUBLISHED]
