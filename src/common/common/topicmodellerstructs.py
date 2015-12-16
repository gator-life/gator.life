#!/usr/bin/env python
# -*- coding: utf-8 -*-


class TopicModellerDocument(object):
    def __init__(self, title, url, topics):
        self.title = title
        self.url = url
        # TODO I think we should replace it by two vectors to operate without deconstructing each tuple pylint: disable=fixme
        self.topics = topics # topics is a list of tuples (topic_label_string, topic_value_double)

