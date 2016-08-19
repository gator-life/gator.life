#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import logging
from time import sleep
import datetime
import jsonpickle
from scraper.scraper import Scraper


def run():
    jsonpickle.set_encoder_options('simplejson', indent=4, ensure_ascii=False)

    scraper = Scraper()

    folder = '/media/nico/SAMSUNG/devs/gator/scraping reddit 10-01-2016'

    log_file = folder + 'run_scraper-' + str(datetime.datetime.utcnow()) + '.log'

    logging.basicConfig(format=u'%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO, filename=log_file)

    while True:
        try:
            for scraper_document in scraper.scrap():
                filename = folder + '/' + str(datetime.datetime.utcnow()) + '.json'
                json = jsonpickle.encode(scraper_document)
                with codecs.open(filename=filename, mode='w', encoding='utf-8') as file_desc:
                    file_desc.write(json)

        except Exception as exception:  # pylint: disable=broad-except
            logging.error("The orchestrator crashed! Starting it over ...")
            logging.exception(exception)
            sleep(30)

run()
