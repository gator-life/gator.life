from gensim import corpora, models, similarities
from itertools import imap
import logging
import nltk
import os

# Initialize logger to see logging events of gensim
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

folder = './training_documents/'

dictionary_file = './dictionary.dic'
corpus_file = './corpus.mm'
lsi_model_file = './model.lsi'
lda_model_file = './model.lda'

# Flatten a list
def flatten_list(l):
    return [j for i in l for j in i]

# Read a document.
def read(folder, file):
    return open(folder + file).read().decode("utf-8").encode("ascii", "ignore")

# Clean document by removing common words etc.
def clean(content):
    return content

# Word "tokenized" documents using NLTK.
def word_tokenize(content):
    return flatten_list([nltk.word_tokenize(sentence) for sentence in nltk.sent_tokenize(content)])

documents = imap(lambda file: word_tokenize(clean(read(folder, file))), os.listdir(folder))

#print(list(documents))

# Construct the mapping Word -> Id
dictionary = corpora.Dictionary(documents)
# Persist the dictionary on disk
dictionary.save(dictionary_file)

#print(dictionary.token2id)

# The iterator need to be reset.
documents = imap(lambda file: word_tokenize(clean(read(folder, file))), os.listdir(folder))

# Construct the Corpus : Transform each document to a vector [(word_id, word_count) | word_count > 0]
corpus = imap(lambda document: dictionary.doc2bow(document), documents)
corpora.MmCorpus.serialize(corpus_file, corpus)

#print(list(corpus))

# Load the dictionary & the corpus
dictionary = corpora.Dictionary.load(dictionary_file)
corpus = corpora.MmCorpus(corpus_file)

# Initialize a TFIDF model
tfidf = models.TfidfModel(corpus)

corpus_tfidf = tfidf[corpus]
#for document in corpus_tfidf:
#    print(document)

# Initialize LSI model
#lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=2)
lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=2)
# Create a double wrapper over the original corpus: Bow -> tfidf -> fold-in-lsi
#corpus_lsi = lsi[corpus_tfidf]
#  Create a wrapper over the original corpus: Bow -> fold-in-lsi
corpus_lsi = lsi[corpus]
#for document in corpus_lsi:
#    print(document)

# Online training
new_document = ['An example of online training document.']
new_document_corpus = map(lambda document: dictionary.doc2bow(word_tokenize(clean(document))), new_document)
lsi.add_documents(new_document_corpus)
lsi_vec = lsi[new_document_corpus] # Convert some new document into the LSI space, Without affecting the model.
#print(list(lsi_vec))

#lsi.print_topics()

lsi.save(lsi_model_file)
lsi = models.LsiModel.load(lsi_model_file)

lda = models.LdaModel(corpus, id2word=dictionary, num_topics=100)
corpus_lda = lda[corpus]
for document in corpus_lda:
    print(document)

lda.save(lda_model_file)
lda = models.LdaModel.load(lda_model_file)
