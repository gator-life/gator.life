#!/usr/bin/env python
# -*- coding: utf-8 -*-

from boilerpipe.extract import Extractor
from gensim import corpora, models
from nltk.corpus import stopwords

import codecs
import datetime
import jsonpickle
import nltk
import os
import re


class TopicModellerDocument(object):
    def __init__(self, url, topics):
        self.url = url
        self.topics = topics


class RepeatableBatchedDocuments(object):
    def __init__(self, folder, batch_size):
        self.folder = folder
        self.batch_size = batch_size

    def __iter__(self):
        documents = []
        for file_name in os.listdir(self.folder):
            (_, document) = _json_sd_file_to_sd_and_tmd(os.path.join(self.folder, file_name))
            documents.append(document)

            if len(documents) == self.batch_size:
                yield documents
                documents = []
        if len(documents) != 0:
            yield documents


class TopicModeller(object):
    def __init__(self):
        self.dictionary = None
        self.dictionary_words = None

        self.lda = None

    def initialize(self, batched_documents, num_topics):
        self._initialize_dictionary(batched_documents)
        self._feed(batched_documents, num_topics)

    def classify(self, document):
        return self.lda[self.dictionary.doc2bow(document)]

    def load(self, model_data_folder):
        dictionary_file_path = self._dictionary_file_path(model_data_folder)
        if os.path.isfile(dictionary_file_path):
            self.dictionary = corpora.Dictionary.load(dictionary_file_path)
            # dictionary.values() is a list, looking into a list is an O(n) operation.
            # To avoid poor performances on _filter_document method, dictionary words
            # are "cached" on a set (O(1)).
            self.dictionary_words = set(self.dictionary.values())
        else:
            raise IOError(u'Dictionary file does not exists : ' + dictionary_file_path)

        lda_file_path = self._lda_file_path(model_data_folder)
        if os.path.isfile(lda_file_path):
            self.lda = models.LdaModel.load(lda_file_path)
        else:
            raise IOError(u'Lda model file does not exists : ' + lda_file_path)

    def save(self, model_data_folder):
        self.dictionary.save(self._dictionary_file_path(model_data_folder))
        self.lda.save(self._lda_file_path(model_data_folder))

    @classmethod
    def _dictionary_file_path(cls, model_data_folder):
        return os.path.join(model_data_folder, 'dictionary.dic')

    @classmethod
    def _lda_file_path(cls, model_data_folder):
        return os.path.join(model_data_folder, 'lda.mod')

    def _initialize_dictionary(self, batched_documents):
        self.dictionary = corpora.Dictionary()

        for documents in batched_documents:
            corpora.Dictionary.add_documents(self.dictionary, documents)

        self.dictionary_words = set(self.dictionary.values())

    def _feed(self, batched_documents, num_topics):
        self.lda = None

        for documents in batched_documents:
            # Construct the Corpus : Transform each document to a vector [(word_id, word_count) | word_count > 0]
            corpus = [self.dictionary.doc2bow(self._filter_document(document)) for document in documents]
            self._update_model(corpus, num_topics)

    def _update_model(self, new_corpus, num_topics):
        if self.lda is None:
            self.lda = models.LdaModel(new_corpus, id2word=self.dictionary, num_topics=num_topics)
        else:
            self.lda.update(new_corpus)

    def _filter_document(self, document):
        # We want to keep only known words (those on our dictionary)
        return [word for word in document if word in self.dictionary_words]


# From JSON to scraper.Document object
def _decode(content):
    return jsonpickle.decode(content)


# Extract a readable document from HTML
def _readable_document(html_document):
    return Extractor(extractor=u'ArticleExtractor', html=html_document).getText()


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


def _json_sd_file_to_sd_and_tmd(file_path):
    # sd : scraper document. tmd ; "topicmodellable" document.
    file_content = open(file_path).read()

    scraper_document = _decode(file_content)

    word_tokenized_document = _word_tokenize(_readable_document(scraper_document.html_content))
    lowercase_document = [word.lower() for word in word_tokenized_document]

    document = _clean(lowercase_document)

    return (scraper_document, document)


def initialize_model(documents_folder, tm_data_folder):
    documents = RepeatableBatchedDocuments(documents_folder, batch_size=2000)

    topicmodeller = TopicModeller()
    topicmodeller.initialize(documents, num_topics=128)
    topicmodeller.save(tm_data_folder)


def classify_and_dump_json(documents_folder, tm_data_folder, output_folder):
    topicmodeller = TopicModeller()
    topicmodeller.load(tm_data_folder)

    jsonpickle.set_encoder_options('simplejson', indent=4, ensure_ascii=False)

    date = datetime.datetime.utcnow()

    for (i, file_name) in enumerate(os.listdir(documents_folder)):
        (scraper_document, document) = _json_sd_file_to_sd_and_tmd(os.path.join(documents_folder, file_name))

        # #pylint: disable=E1101
        json = jsonpickle.encode(TopicModellerDocument(scraper_document.link_element.url, topicmodeller.classify(document)))
        # #pylint: enable=E1101
        filename = os.path.join(output_folder, str(date) + '_' + str(i) + '.json')
        with codecs.open(filename=filename, mode='w', encoding='utf-8') as file_desc:
            file_desc.write(json)
