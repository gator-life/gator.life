# -*- coding: utf-8 -*-

from boilerpipe.extract import Extractor
from gensim import corpora, models
from itertools import chain
from nltk.corpus import stopwords

import jsonpickle
import nltk
import os


class TopicModellerDocument(object):
    def __init__(self, scrapper_document, topics):
        self.scrapper_document = scrapper_document
        self.topics = topics


# Gensim LdaModel need a repeatable stream of corpus
class RepeatableImap(object):
    def __init__(self, function, iterable):
        self.function = function
        self.iterable = iterable

    def __iter__(self):
        for element in self.iterable:
            yield self.function(element)


class RepeatableBatchedDocuments(object):
    # From JSON to 2-tuple (scraper.document, readable, cleaned, word tokenized documents)
    def __init__(self, folder, batch_size):
        self.folder = folder
        self.batch_size = batch_size

    def __iter__(self):
        documents = []
        for file_name in os.listdir(self.folder):

            document_content = open(os.path.join(self.folder, file_name)).read()
            scraper_document = _decode(document_content)
            readable_document = _readable_document(scraper_document.html_content)
            # documents.append((scraper_document, _clean(_word_tokenize(readable_document))))
            documents.append(_clean(_word_tokenize(readable_document)))

            if len(documents) == self.batch_size:
                yield documents
                documents = []
        if len(documents) != 0:
            yield documents


class TopicModeller(object):
    def __init__(self, model_data_folder, topics):
        self.model_data_folder = model_data_folder

        self.dictionary_file = os.path.join(model_data_folder, 'dictionary.dic')
        self.corpus_file = os.path.join(model_data_folder, 'corpus.cor')
        self.lda_model_file = os.path.join(model_data_folder, 'lda.mod')

        self.topics = topics

        self.corpus = None
        self.lda = None

        if os.path.isfile(self.dictionary_file):
            self.dictionary = corpora.Dictionary.load(self.dictionary_file)

        if os.path.isfile(self.corpus_file):
            self.corpus = corpora.MmCorpus(self.corpus_file)

        if os.path.isfile(self.lda_model_file):
            self.lda = models.LdaModel.load(self.lda_model_file)

    def initialize_dictionary(self, batched_documents):
        # Construct the mapping Word -> Id
        self.dictionary = corpora.Dictionary()
        for documents in batched_documents:
            corpora.Dictionary.add_documents(self.dictionary, documents)
        self.dictionary.save(self.dictionary_file)

        self.corpus = None
        self.lda = None

    def feed(self, batched_documents):
        for documents in batched_documents:
            corpus = self.__update_corpus(documents)
            self.__update_model(corpus)
        corpora.MmCorpus.serialize(self.corpus_file, self.corpus)
        self.lda.save(self.lda_model_file)

    def classify(self, document):
        return self.lda[self.dictionary.doc2bow(document)]

    def __update_corpus(self, documents):
        # Construct the Corpus : Transform each document to a vector [(word_id, word_count) | word_count > 0]
        corpus = RepeatableImap(lambda document: self.dictionary.doc2bow(self.__filter_document(document)), documents)
        self.corpus = chain(self.corpus, corpus) if self.corpus is not None else corpus

        return corpus

    def __update_model(self, corpus):
        # Construct the LDA model
        if self.lda is None:
            self.lda = models.LdaModel(corpus, id2word=self.dictionary, num_topics=self.topics)
        else:
            self.lda.update(corpus)

    def __filter_document(self, document):
        # We want to keep only known words (those on our dictionary)
        return [word for word in document if word in self.dictionary.values()]


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
    return words

# TODO
# - Add __len__ method to RepeatableBatchedDocuments class.
# - Understand why corpus is not updated with the new feeded data.
# - Filter words by keeping only latin words
# - Generate TopicModellerDocument(s).
# - Understand why the feed process is so long.