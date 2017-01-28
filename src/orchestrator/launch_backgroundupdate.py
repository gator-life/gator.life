#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common.log import init_gcloud_log
from common.environment import GCLOUD_PROJECT
from orchestrator.backgroundupdate import update_model_profiles_userdocs

init_gcloud_log(GCLOUD_PROJECT, u'background_update')
update_model_profiles_userdocs()
