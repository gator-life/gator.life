import re
import nltk
from nltk.corpus import stopwords
from boilerpipe.extract import Extractor


# Extract a readable document from HTML
def _readable_document(html_document):
    extractor = Extractor(extractor=u'ArticleExtractor', html=html_document)
    text = extractor.getText()
    return text


def _word_tokenize(content):
    word_tokenized = []
    for sentence in nltk.sent_tokenize(content):
        word_tokenized += nltk.word_tokenize(sentence)
    return word_tokenized


def _clean(words):
    return _filter_latin_words(_remove_stop_words(words))


def _remove_stop_words(words):
    return [word for word in words if word not in stopwords.words('english')]


def _filter_latin_words(words):
    return [word for word in words if re.search(r'^[a-zA-Z]*$', word) is not None]


class DocTokenizer(object):
    @classmethod
    def tokenize(cls, html_document):
        word_tokenized_document = _word_tokenize(_readable_document(html_document))
        lowercase_document = [word.lower() for word in word_tokenized_document]
        document = _clean(lowercase_document)
        return document
