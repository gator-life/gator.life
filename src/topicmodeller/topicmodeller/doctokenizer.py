# -*- coding: utf-8 -*-

import logging
import re
import nltk
from nltk.corpus import stopwords
from common.log import shrink

LOGGER = logging.getLogger(__name__)


def _word_tokenize(content):
    word_tokenized = []
    for sentence in nltk.sent_tokenize(content):
        word_tokenized += nltk.word_tokenize(sentence)
    return word_tokenized


def _clean(words):
    return _filter_latin_words(_remove_stop_words(words))


def _remove_stop_words(words):
    english_words = set(stopwords.words('english'))  # don't inline call in for loop: (long complex call)
    return [word for word in words if word not in english_words]


def _filter_latin_words(words):
    return [word for word in words if re.search(r'^[a-zA-Z]*$', word) is not None]


class DocTokenizer(object):

    @classmethod
    def tokenize(cls, raw_text):
        word_tokenized_document = _word_tokenize(raw_text)
        lowercase_document = [word.lower() for word in word_tokenized_document]
        tokens = _clean(lowercase_document)
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug(u'html tokenized. tokens[%s], text[%s]',
                         u'|'.join(tokens[:50]), shrink(raw_text))
        return tokens
