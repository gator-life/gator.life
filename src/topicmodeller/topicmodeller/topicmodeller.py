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
        scraper_documents = []
        documents = []
        for file_name in os.listdir(self.folder):

            file_content = open(os.path.join(self.folder, file_name)).read()
            scraper_document = _decode(file_content)
            readable_document = _readable_document(scraper_document.html_content)

            scraper_documents.append(scraper_document)
            documents.append(_clean(_word_tokenize(readable_document)))

            if len(documents) == self.batch_size:
                yield (scraper_documents, documents)
                scraper_documents = []
                documents = []
        if len(documents) != 0:
            yield (scraper_documents, documents)


class TopicModeller(object):
    def __init__(self, model_data_folder, topics):
        self.model_data_folder = model_data_folder

        self.dictionary_file = os.path.join(model_data_folder, 'dictionary.dic')
        self.lda_model_file = os.path.join(model_data_folder, 'lda.mod')

        self.topics = topics

        self.lda = None

        if os.path.isfile(self.dictionary_file):
            self.dictionary = corpora.Dictionary.load(self.dictionary_file)
            # dictionary.values() is a list, looking into a list is an O(n) operation.
            # To avoid poor performances on __filter_document method, dictionary words
            # are "cached" on a set (O(1)).
            self.dictionary_words = set(self.dictionary.values())

        if os.path.isfile(self.lda_model_file):
            self.lda = models.LdaModel.load(self.lda_model_file)

    def initialize_dictionary(self, batched_documents):
        self.dictionary = corpora.Dictionary()

        for (_, documents) in batched_documents:
            corpora.Dictionary.add_documents(self.dictionary, documents)
        self.dictionary.save(self.dictionary_file)

        self.dictionary_words = set(self.dictionary.values())

        self.lda = None

    def feed(self, batched_documents):
        for (_, documents) in batched_documents:
            # Construct the Corpus : Transform each document to a vector [(word_id, word_count) | word_count > 0]
            corpus = [self.dictionary.doc2bow(self.__filter_document(document)) for document in documents]
            self.__update_model(corpus)
        self.lda.save(self.lda_model_file)

    def classify(self, document):
        return self.lda[self.dictionary.doc2bow(document)]

    def __update_model(self, new_corpus):
        if self.lda is None:
            self.lda = models.LdaModel(new_corpus, id2word=self.dictionary, num_topics=self.topics)
        else:
            self.lda.update(new_corpus)

    def __filter_document(self, document):
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
    return [word for word in words if re.search(r'^[a-zA-Z\-\']*$', word) is not None]


def initialize_model(documents_folder, tm_data_folder):
    documents = RepeatableBatchedDocuments(documents_folder, 2000)

    topicmodeller = TopicModeller(tm_data_folder, 128)

    topicmodeller.initialize_dictionary(documents)
    topicmodeller.feed(documents)


def classify_and_dump_json(documents_folder, tm_data_folder, output_folder):
    topicmodeller = TopicModeller(tm_data_folder, 128)

    jsonpickle.set_encoder_options('simplejson', indent=4, ensure_ascii=False)

    documents = RepeatableBatchedDocuments(documents_folder, 2000)

    tm_documents = (TopicModellerDocument(scraper_document.link_element.url, topicmodeller.classify(document))
                    for (batched_scraper_documents, batched_documents) in documents
                    for (scraper_document, document) in zip(batched_scraper_documents, batched_documents))

    date = datetime.datetime.utcnow()

    for (i, tm_document) in enumerate(tm_documents):
        json = jsonpickle.encode(tm_document)
        filename = os.path.join(output_folder, str(date) + '_' + str(i) + '.json')
        with codecs.open(filename=filename, mode='w', encoding='utf-8') as file_desc:
            file_desc.write(json)
