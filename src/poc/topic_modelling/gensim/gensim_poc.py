from common import scraperstructs
from boilerpipe.extract import Extractor
from gensim import corpora, models, similarities
from itertools import imap, chain
import jsonpickle
import logging
import lxml.html
import nltk
import os

# Initialize logger to see logging events of gensim
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

documents_folder = './documents/'

dictionary_file = './data/dictionary.dic'
corpus_file = './data/corpus.mm'

lda_model_file = './data/model.lda'

# How much different topics they are ?
topics = 40


# A repeatable imap class :
# - We need to iterate multiple time through documents.
# - Gensim LdaModel need a repeatable stream of corpus
class RepeatableImap(object):
    def __init__(self, function, iterable):
        self.function = function
        self.iterable = iterable

    def __iter__(self):
        for it in self.iterable:
            yield self.function(it)


# Flatten a list
def _flatten_list(l):
    return [j for i in l for j in i]


# Read a document.
def _read(folder, file_name):
    return open(folder + file_name).read().decode("utf-8").encode("ascii", "ignore")


# From JSON to scraper.Document object
def _decode(content):
    return jsonpickle.decode(content).html_content


# Extract a readable document from HTML
def _readable_document(content):
    return Extractor(extractor='ArticleExtractor', html=content).getText()


# Clean by removing common words etc.
def _clean(content):
    return content


# Word "tokenized" using NLTK.
def _word_tokenize(content):
    return _flatten_list([nltk.word_tokenize(sentence) for sentence in nltk.sent_tokenize(content)])


def update_model():
    documents = RepeatableImap(lambda file_name: _word_tokenize(_clean(_readable_document(_decode(
        _read(documents_folder, file_name))))), os.listdir(documents_folder))

    if os.path.isfile(dictionary_file):
        # Load the dictionary
        dictionary = corpora.Dictionary.load(dictionary_file)
        corpora.Dictionary.add_documents(dictionary, documents)
    else:
        # Construct the mapping Word -> Id
        dictionary = corpora.Dictionary(documents)
    # Persist the dictionary
    dictionary.save(dictionary_file)

    # Construct the Corpus : Transform each document to a vector [(word_id, word_count) | word_count > 0]
    corpus = RepeatableImap(lambda document: dictionary.doc2bow(document), documents)
    if os.path.isfile(corpus_file):
        # Load the corpus & update it with the new corpus
        updated_corpus = chain(corpora.MmCorpus(corpus_file), corpus)
    else:
        updated_corpus = corpus
    # Persist the updated corpus
    corpora.MmCorpus.serialize(corpus_file, updated_corpus)

    if os.path.isfile(lda_model_file):
        lda = models.LdaModel.load(lda_model_file)
        lda.update(corpus)
    else:
        lda = models.LdaModel(corpus, id2word=dictionary, num_topics=topics)
    # Persist the model
    lda.save(lda_model_file)


classification_dictionary = None
classification_lda = None


def classify_document(document):
    global classification_dictionary, classification_lda

    if classification_dictionary is None and classification_lda is None:
        if not os.path.isfile(dictionary_file) or not os.path.isfile(lda_model_file):
            raise RuntimeError("Model files not found. Call update_model() to generate them.")

        classification_dictionary = corpora.Dictionary.load(dictionary_file)
        classification_lda = models.LdaModel.load(lda_model_file)

    return classification_lda[classification_dictionary.doc2bow(_word_tokenize(_clean(_readable_document(
        _decode(document)))))]


update_model()
# for file_name in os.listdir(documents_folder):
#     content = _read(documents_folder, file_name)
#     scraper_document = jsonpickle.decode(content)
#     print file_name
#     print "\tTitle: " + scraper_document.link_element.origin_info.title
#     print "\tTopic(s): " + str(classify_document(content)) + "\n"
