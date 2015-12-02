#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import nltk
from nltk.corpus import stopwords

from boilerpipe.extract import Extractor
from gensim import corpora, models
from common.topicmodellerstructs import TopicModellerDocument


class TopicModellableDocuments(object):
    def __init__(self, documents):
        self.documents = documents

    def __iter__(self):
        for document in self.documents:
            yield _to_topicmodellable_document(document)


class TopicModeller(object):
    corpus_batch_size = 250

    def __init__(self):
        self.dictionary = None
        self.dictionary_words = None

        self.lda = None

        self.topics = None

    def initialize(self, documents, num_topics):
        # The dictionary must be fully initialized before "feeding" the model.
        self._initialize_dictionary(documents)
        self._feed(documents, num_topics)

    def classify(self, document):
        classification = dict(
            # weight.item() : from numpy float64 object to python native float.
            ((topic_id, weight.item()) for (topic_id, weight)
             in self.lda[self.dictionary.doc2bow(self._filter_document(document))])
        )

        # Generate a vector of [(topic_id, weight) | for each topic_id in topics]
        vector = []
        for (topic_id, _) in self.topics:
            weight = classification.get(topic_id, 0)
            vector.append((topic_id, weight))

        return vector

    def load(self, model_data_folder):
        dictionary_file_path = self._dictionary_file_path(model_data_folder)
        if os.path.isfile(dictionary_file_path):
            self.dictionary = corpora.Dictionary.load(dictionary_file_path)
        else:
            raise IOError(u'Dictionary file does not exists : ' + dictionary_file_path)

        lda_file_path = self._lda_file_path(model_data_folder)
        if os.path.isfile(lda_file_path):
            self.lda = models.LdaModel.load(lda_file_path)
        else:
            raise IOError(u'Lda model file does not exists : ' + lda_file_path)

        self._cache_dictionary_words()
        self._cache_topics()

    def save(self, model_data_folder):
        self.dictionary.save(self._dictionary_file_path(model_data_folder))
        self.lda.save(self._lda_file_path(model_data_folder))

    @classmethod
    def _dictionary_file_path(cls, model_data_folder):
        return os.path.join(model_data_folder, 'dictionary.dic')

    @classmethod
    def _lda_file_path(cls, model_data_folder):
        return os.path.join(model_data_folder, 'lda.mod')

    def _initialize_dictionary(self, documents):
        self.dictionary = corpora.Dictionary()
        corpora.Dictionary.add_documents(self.dictionary, documents)

    def _feed(self, documents, num_topics):
        corpus = []
        for document in documents:
            # Construct the Corpus : Transform each document to a vector [(word_id, word_count) | word_count > 0]
            corpus.append(self.dictionary.doc2bow(document))
            if len(corpus) == self.corpus_batch_size:
                self._update_model(corpus, num_topics)
                corpus = []

        if len(corpus) != 0:
            self._update_model(corpus, num_topics)

    def _update_model(self, new_corpus, num_topics):
        if self.lda is None:
            self.lda = models.LdaModel(new_corpus, id2word=self.dictionary, num_topics=num_topics)
        else:
            self.lda.update(new_corpus)

    def _filter_document(self, document):
        # We want to keep only known words (those on our dictionary)
        return [word for word in document if word in self.dictionary_words]

    def _cache_dictionary_words(self):
        # dictionary.values() is a list, looking into a list is an O(n) operation.
        # To avoid poor performances on _filter_document method, dictionary words
        # are "cached" on a set (O(1)).
        self.dictionary_words = set(self.dictionary.values())

    def _cache_topics(self):
        self.topics = [(i, [word for (_, word) in self.lda.show_topic(topicid=i, topn=1)])
                       for i in range(self.lda.num_topics)]


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


def _to_topicmodellable_document(scraper_document):
    word_tokenized_document = _word_tokenize(_readable_document(scraper_document.html_content))
    lowercase_document = [word.lower() for word in word_tokenized_document]

    document = _clean(lowercase_document)

    return document


def initialize_model(scraper_documents, tm_data_folder, num_topics):
    topicmodeller = TopicModeller()
    topicmodeller.initialize(TopicModellableDocuments(scraper_documents), num_topics)
    topicmodeller.save(tm_data_folder)


def classify(topicmodeller, scraper_document):
    document = _to_topicmodellable_document(scraper_document)

    return TopicModellerDocument(scraper_document.link_element.origin_info.title,
                                 scraper_document.link_element.url,
                                 topicmodeller.classify(document))
