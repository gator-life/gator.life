# -*- coding: utf-8 -*-

from datetime import datetime
import pytz


def utcnow():
    """
    datetime.utcnow() returns by default a timezone unaware datetime (without timezone info),
    but datetime returned by gcloud datastore is timezone aware, so a comparison between the two fails
    :return: timezone aware version of datetime.utcnow()
    """
    return datetime.utcnow().replace(tzinfo=pytz.utc)
