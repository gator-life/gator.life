import praw
import urllib3.contrib.pyopenssl
from itertools import ifilter, imap
from common.scraperstructs import LinkElement, OriginInfo

def reddit_link_elements_generator(disconnected):
    submissions = _make_submissions_generator(disconnected)
    filtered_submissions = ifilter(_is_valid_submission, submissions)
    link_elts = imap(_make_link_element, filtered_submissions)
    return link_elts

def _make_submissions_generator(disconnected):
    request_interval = 0 if disconnected else 2 # disconnected if we run with vcrpy, no need to delay requests
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
    url = submission.url.encode('utf8')
    origin_name = u'reddit'
    title = submission.title.encode('utf8')
    category = submission.subreddit.display_name.encode('utf8')
    origin_url = submission.permalink.encode('utf8')
    origin_id = submission.id.encode('utf8')
    category_id = submission.subreddit_id.encode('utf8')
    origin_info = OriginInfo(title, category, origin_url, origin_id, category_id)
    date_as_utc_timestamp = submission.created_utc
    link_elt = LinkElement(url, origin_name, origin_info, date_as_utc_timestamp)
    return link_elt
