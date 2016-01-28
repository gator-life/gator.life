#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from orchestrator.scrap_and_learn import scrap_and_learn
from common.JsonDocLoader import JsonDocLoader
from common.JsonDocSaver import JsonDocSaver
from common.remote_api import initialize_remote_api
from scraper.scraper import Scraper
from topicmodeller.topicmodeller import TopicModeller


logging.basicConfig(format=u'%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO, filename='scrap_and_learn.log')


class FileLoaderScraper(object):
    def __init__(self, folder):
        self.scraper_docs = JsonDocLoader(folder)
    def scrap(self):
        for scraper_document in self.scraper_docs:
            yield scraper_document


class NoActionSaver(object):
    def save(self, doc):
        pass


def launch_scrap_and_learn(scraper, doc_saver, tm_data_folder):
    user_docs_max_size = 30
    docs_chunk_size = 1000

    topic_modeller = TopicModeller.make()
    topic_modeller.load(tm_data_folder)

    scrap_and_learn(scraper, doc_saver, topic_modeller, docs_chunk_size, user_docs_max_size)


def launch_by_scraping(scraper_output_folder, tm_data_folder):
    scraper = Scraper()
    doc_saver = JsonDocSaver(scraper_output_folder)

    launch_scrap_and_learn(scraper, doc_saver, tm_data_folder)


def launch_by_folder(scraper_documents_folder, tm_data_folder):
    scraper = FileLoaderScraper(scraper_documents_folder)
    doc_saver = NoActionSaver()
    launch_scrap_and_learn(scraper, doc_saver, tm_data_folder)


initialize_remote_api()

launch_by_folder('/home/mohamed/Development/Data/gator/Scraping_11-01-2016_Snapshot',
                      '/home/mohamed/Development/Data/gator/TopicModellerData')
