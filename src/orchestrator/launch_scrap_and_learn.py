#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from orchestrator.scrap_and_learn import scrap_and_learn

logging.basicConfig(format=u'%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO, filename='scrap_and_learn.log')

scrap_and_learn()
