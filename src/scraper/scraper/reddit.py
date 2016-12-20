# -*- coding: utf-8 -*-

import logging
import praw
import urllib3.contrib.pyopenssl

LOGGER = logging.getLogger(__name__)


class OriginInfo(object):
    """
    info extracted from the origin (reddit...) related to the current linkElement
    """

    def __init__(self, title, category, url, unique_id, category_id):
        """
        :param title: string
        :param category: string
        :param url: string of the url where link has been extracted
        :param unique_id: string identifier of the link in the origin referential
        :param category_id: string identifier of the category of the link in the origin referential
        :return:
        """
        self.title = title
        self.category = category
        self.url = url
        self.unique_id = unique_id
        self.category_id = category_id


class LinkElement(object):

    def __init__(self, url, origin, origin_info, date_utc_timestamp):
        """
        :param url: string of the url
        :param origin: string (label) of the origin (ie: 'reddit')
        :param origin_info: OriginInfo
        :param date_utc_timestamp: date in second from the unix epoch
        :return:
        """
        self.url = url
        self.origin = origin
        self.origin_info = origin_info
        self.date_utc_timestamp = date_utc_timestamp


def reddit_link_elements_generator(disconnected):
    submissions = _make_submissions_generator(disconnected)
    for submission in submissions:
        if _is_valid_submission(submission):
            try:
                elt = _make_link_element(submission)
                LOGGER.debug('yield link elt, url[%s]', elt.url)
                yield elt
            except UnicodeError:
                LOGGER.info(u'unicode error in submission')


def _make_submissions_generator(disconnected):
    if disconnected:
        request_interval = 0  # disconnected if we run with vcrpy, no need to delay requests
        # praw return cache if same page is hit below 30s. This causes issues between several unit tests (using different
        # vcr cassette) as praw return response of a previous test, the line below clears this cache
        # cf. http://praw.readthedocs.io/en/stable/pages/faq.html?highlight=cache
        praw.handlers.DefaultHandler.clear_cache()
    else:
        request_interval = 2  # pragma: no cover

    # bug on me PC, see https://urllib3.readthedocs.org/en/latest/security.html section OpenSSL / PyOpenSSL
    urllib3.contrib.pyopenssl.inject_into_urllib3()
    reddit_agent = praw.Reddit(user_agent='gator_reddit_client', check_for_updates=False, api_request_delay=request_interval)
    all_subreddit = reddit_agent.get_subreddit('all')
    submissions = all_subreddit.get_new(limit=None)
    return submissions


def _is_valid_submission(submission):
    if submission.is_self:
        return False
    if submission.over_18:
        return False
    return True


def _make_link_element(submission):
    url = submission.url.decode('utf8')
    origin_name = u'reddit'
    title = submission.title.decode('utf8')
    category = submission.subreddit.display_name.decode('utf8')
    origin_url = submission.permalink.decode('utf8')
    origin_id = submission.id.decode('utf8')
    category_id = submission.subreddit_id.decode('utf8')
    origin_info = OriginInfo(title, category, origin_url, origin_id, category_id)
    date_as_utc_timestamp = submission.created_utc
    link_elt = LinkElement(url, origin_name, origin_info, date_as_utc_timestamp)
    return link_elt
