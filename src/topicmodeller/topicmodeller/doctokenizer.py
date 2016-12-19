# -*- coding: utf-8 -*-

import logging
import re
import nltk
from nltk.corpus import stopwords
from readability import Document
import lxml
from common.log import shrink

LOGGER = logging.getLogger(__name__)


def _readable_document(html_document):
    readability_doc = Document(html_document)
    text_without_useless_parts = readability_doc.summary()
    text_without_html_markup = lxml.html.fromstring(text_without_useless_parts).text_content()
    return text_without_html_markup


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


class DocTokenizerFromHtml(object):

    @classmethod
    def tokenize(cls, html_document):
        raw_text = _readable_document(html_document)
        tokens = DocTokenizerFromRawText.tokenize(raw_text)
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug(u'html tokenized. tokens[%s], text[%s], html[%s]',
                         u'|'.join(tokens[:50]), shrink(raw_text), shrink(html_document))
        return tokens


class DocTokenizerFromRawText(object):

    @classmethod
    def tokenize(cls, raw_text):
        word_tokenized_document = _word_tokenize(raw_text)
        lowercase_document = [word.lower() for word in word_tokenized_document]
        document = _clean(lowercase_document)
        return document
