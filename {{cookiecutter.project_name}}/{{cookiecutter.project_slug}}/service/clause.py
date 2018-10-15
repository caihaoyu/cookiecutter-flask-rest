import spacy
from textrank4zh.Segmentation import SentenceSegmentation


class ClauseArticle():
    def __init__(self):
        self.seger = SentenceSegmentation()
        self.max_words = 140

    def sents_content(self, content):
        """
        将中文文章的正文分句，并抽取摘要

        @param content: 中文文章正文
        @type content: str
        @return: 分好句的正文，抽取的中文摘要
        @rtype: str, str
        """
        content_list = []
        summary_list = []
        article_content = self.seger.segment(content)
        for sentence in article_content:
            sentence = sentence + '。'
            content_list.append(sentence)
        if len(''.join(content_list)) <= self.max_words:
            return ('\n\n'.join(content_list),
                    ''.join(content_list))
        else:
            for sentences in content_list:
                summary_list.append(sentences)
                if len(''.join(summary_list)) > self.max_words:
                    return ('\n\n'.join(content_list),
                            ''.join(summary_list))

    def sents(self, text):
        """
        英文分句功能

        @param text: 需要分句的英文正文
        @type text: str
        @return : 分好句的正文用 '\n\n' 隔开
        @rtype: str
        """
        nlp = spacy.load('en_core_web_sm')
        text = text.replace('\r', '').replace('\n', '')
        text = text.replace('"', '“').replace('"', '”')
        doc = nlp(text)
        return '\n\n'.join(map(str, list(doc.sents)))
