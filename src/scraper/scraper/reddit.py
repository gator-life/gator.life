# -*- coding: utf-8 -*-

import praw
import urllib3.contrib.pyopenssl
from .scraperstructs import LinkElement, OriginInfo


def reddit_link_elements_generator(disconnected):
    submissions = _make_submissions_generator(disconnected)
    for submission in submissions:
        if _is_valid_submission(submission):
            try:
                elt = _make_link_element(submission)
                yield elt
            except UnicodeError:
                pass


def _make_submissions_generator(disconnected):
    if disconnected:
        request_interval = 0  # disconnected if we run with vcrpy, no need to delay requests
        # praw return cache if same page is hit below 30s. This causes issues between several unit tests (using different
        # vcr cassette) as praw return response of a previous test, the line below clears this cache
        # cf. http://praw.readthedocs.io/en/stable/pages/faq.html?highlight=cache
        praw.handlers.DefaultHandler.clear_cache()
    else:
        request_interval = 2

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
