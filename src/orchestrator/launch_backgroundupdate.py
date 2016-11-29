#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common.log import init_gcloud_log
from orchestrator.backgroundupdate import update_model_profiles_userdocs
from server.environment import IS_TEST_ENV, GCLOUD_PROJECT

init_gcloud_log(GCLOUD_PROJECT, u'background_update', IS_TEST_ENV)
update_model_profiles_userdocs()
