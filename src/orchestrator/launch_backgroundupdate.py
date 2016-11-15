#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from orchestrator.backgroundupdate import update_model_profiles_userdocs

logging.basicConfig(format=u'%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO, filename='scrap_and_learn.log')

update_model_profiles_userdocs()
