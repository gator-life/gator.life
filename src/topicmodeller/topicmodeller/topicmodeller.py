#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
from gensim import corpora, models
from .doctokenizer import DocTokenizer


class TopicModeller(object):
    corpus_batch_size = 250

    @classmethod
    def make(cls):
        return TopicModeller(DocTokenizer())

    # constructor allowing injection of custom tokenizer
    def __init__(self, document_tokenizer):
        self._dictionary = None
        self._dictionary_words = None
        self._lda = None
        self.topics = None
        self._tokenizer = document_tokenizer
        np.random.seed(2406834896)  # to get reproductible results
        # nb: ideally gensim should allow to inject RandomState to not make side effects on other libs using numpy RNG

    def initialize(self, documents, num_topics):
        """
        Build/calibrate the topic modeller model, set the "topics" field.
        The model can then be saved of used for classification
        :param documents: corpus used by the model to build the model, as a generator of string
        :param num_topics: number of topics to generate
        """
        self.initialize_dictionary(documents)
        self.initialize_model(documents, num_topics)

    def initialize_model(self, documents, num_topics):
        for_feed_generator = (self._tokenizer.tokenize(document_content) for document_content in documents)
        self._feed(for_feed_generator, num_topics)
        self._cache_topics()

    def initialize_dictionary(self, documents):
        for_dict_generator = (self._tokenizer.tokenize(document_content) for document_content in documents)
        self._initialize_dictionary(for_dict_generator)
        self._cache_dictionary_words()

    def classify(self, html_document):
        """
        Do the topic classification of the document
        :param html_document: html document as a string
        :return: float vector of the size of TopicModeller.topics. Each value measure the significance of the associated
         topic for this document
        """
        tokenized_doc = self._tokenizer.tokenize(html_document)
        filtered_doc = self._filter_document(tokenized_doc)
        doc_format_for_lda_model = self._dictionary.doc2bow(filtered_doc)
        # self.lda LdaModel []-operator return list of (topic_id, topic_probability) 2-tuples
        topic_id_weight_dict = dict(self._lda[doc_format_for_lda_model])
        return [topic_id_weight_dict.get(topic_id, 0) for (topic_id, _) in self.topics]

    def load(self, model_data_folder):
        """
        Deserialize a previously saved model
        :param model_data_folder: folder where the model has been saved
        """
        self.load_dictionary(model_data_folder)
        self.load_model(model_data_folder)

    def load_model(self, model_data_folder):
        lda_file_path = self._lda_file_path(model_data_folder)
        if os.path.isfile(lda_file_path):
            self._lda = models.LdaModel.load(lda_file_path)
            self._cache_topics()
        else:
            raise IOError(u'Lda model file does not exists : ' + lda_file_path)

    def load_dictionary(self, model_data_folder):
        dictionary_file_path = self._dictionary_file_path(model_data_folder)
        if os.path.isfile(dictionary_file_path):
            self._dictionary = corpora.Dictionary.load(dictionary_file_path)
            self._cache_dictionary_words()
        else:
            raise IOError(u'Dictionary file does not exists : ' + dictionary_file_path)

    def save(self, model_data_folder):
        """
        Serialize the model previously calibrated by the initialize function
        :param model_data_folder: folder where to serialize the model
        """
        self.save_dictionary(model_data_folder)
        self.save_model(model_data_folder)

    def save_model(self, model_data_folder):
        self._lda.save(self._lda_file_path(model_data_folder))

    def save_dictionary(self, model_data_folder):
        self._dictionary.save(self._dictionary_file_path(model_data_folder))

    @classmethod
    def _dictionary_file_path(cls, model_data_folder):
        return os.path.join(model_data_folder, 'dictionary.dic')

    @classmethod
    def _lda_file_path(cls, model_data_folder):
        return os.path.join(model_data_folder, 'lda.mod')

    def _initialize_dictionary(self, tokenized_documents):
        self._dictionary = corpora.Dictionary()
        corpora.Dictionary.add_documents(self._dictionary, tokenized_documents)
        # memory is O(size(_dictionary) * nb_topics), filter_extremes removes irrelevant words (too rare or too frequent)
        self._dictionary.filter_extremes()

    def _feed(self, documents, num_topics):
        corpus = []
        for document in documents:
            # Construct the Corpus : Transform each document to a vector [(word_id, word_count) | word_count > 0]
            corpus.append(self._dictionary.doc2bow(document))
            if len(corpus) == self.corpus_batch_size:
                self._update_model(corpus, num_topics)
                corpus = []

        if len(corpus) != 0:
            self._update_model(corpus, num_topics)

    def _update_model(self, new_corpus, num_topics):
        if self._lda is None:
            self._lda = models.LdaModel(new_corpus, id2word=self._dictionary, num_topics=num_topics)
        else:
            self._lda.update(new_corpus)

    def _filter_document(self, document):
        # We want to keep only known words (those on our dictionary)
        return [word for word in document if word in self._dictionary_words]

    def _cache_dictionary_words(self):
        # dictionary.values() is a list, looking into a list is an O(n) operation.
        # To avoid poor performances on _filter_document method, dictionary words
        # are "cached" on a set (O(1)).
        self._dictionary_words = set(self._dictionary.values())

    def _cache_topics(self):
        self.topics = [(i, [word for (word, _) in self._lda.show_topic(topicid=i, topn=1)])
                       for i in range(self._lda.num_topics)]
