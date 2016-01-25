#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import datetime
import jsonpickle

class JsonDocSaver(object):
    def __init__(self, folder):
        self.folder = folder

        # set unicode and pretty-print
        jsonpickle.set_encoder_options('simplejson', indent=4, ensure_ascii=False)

    def save(self, document):
        json = jsonpickle.encode(document)
        filename = self.folder + '/' + str(datetime.datetime.utcnow()) + '.json'
        with codecs.open(filename=filename, mode='w', encoding='utf-8') as file_desc:
            file_desc.write(json)
