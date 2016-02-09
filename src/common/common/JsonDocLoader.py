#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import jsonpickle


class JsonDocLoader(object):

    def __init__(self, folder):
        self.folder = folder

    def __iter__(self):
        for file_name in os.listdir(self.folder):
            file_path = os.path.join(self.folder, file_name)
            logging.info('JSON Pickling: ' + file_path)

            try:
                file_content = open(file_path).read()
                yield jsonpickle.decode(file_content)
            except Exception as exception:  # pylint: disable=broad-except
                logging.error("Unable to JSON pickle file: " + file_path, exception)
                continue
