# -*- coding: utf-8 -*-

import re
import os
import socket
import ssl
import logging
import urlparse
import cchardet
import requests

from .reddit import reddit_link_elements_generator
from .scraperstructs import Document

LOGGER = logging.getLogger(__name__)


def _is_valid_link(link_element, invalid_paths_regex, invalid_extensions):
    url = link_element.url
    path = urlparse.urlparse(url).path
    extension = os.path.splitext(path)[1]  # splitext split in two : path and extension
    if extension in invalid_extensions:
        return False
    invalid_path_found = invalid_paths_regex.search(url)
    if invalid_path_found:
        return False
    return True


class _HtmlExtractor(object):

    def __init__(self):
        # set field instead of direct static call to be able to mock/override imported 'requests' module in some tests
        self._requests = requests

    def try_get_html(self, url):
        try:
            LOGGER.debug('get html from url[%s]', url)
            data = self._requests.get(url, timeout=2)  # make the http request
            header_encoding = data.encoding
            if not header_encoding:
                LOGGER.info('filtered: no header encoding, url:%s', url)
                return None
            # cchardet way faster than data.apparent_encoding
            # https://github.com/kennethreitz/requests/issues/2359
            guessed_encoding = cchardet.detect(data.content)['encoding'].lower()
            if guessed_encoding is None or header_encoding.lower() != guessed_encoding:
                LOGGER.info(
                    'filtered: guessed encoding %s different from header encoding %s, url:%s',
                    guessed_encoding, header_encoding, url)
                return None
            data.content.decode(guessed_encoding)  # check we can get unicode object from raw data (could raise exception)
            if not self._is_size_reasonable(data.text):
                LOGGER.info('filtered: size too big, url:%s', url)
                return None
            return data.text
        except (
                ssl.SSLError,
                socket.timeout,
                UnicodeDecodeError,
                requests.exceptions.RequestException
        ) as expected_exception:
            LOGGER.warning('managed exception, url[%s], exception[%s]', url, expected_exception)
            return None
        except Exception:  # pylint: disable=broad-except
            #  to not crash the whole process...
            LOGGER.exception('unexpected exception, url[%s]', url)
            return None

    @classmethod
    def _is_size_reasonable(cls, text):
        return len(text) < 1000000


def _get_invalid_regex():
    invalid_path_video = ['youtu', 'vimeo', 'vid.me', 'tube', 'gfycat', 'vine', 'motion', 'twitch', 'stream', 'video']
    invalid_path_image = ['img', 'flickr', 'flic.kr', 'instagram', 'image', 'imgreview', 'screencloud', 'prnt']
    invalid_path_sound = ['itune', 'soundcloud', 'gifsound', 'spotify']
    invalid_path_social_network = ['twitter', 'facebook']
    invalid_path_aggregator = ['reddit', 'redd.it', 'tumblr', 'voat']
    invalid_path_store = ['ebay', 'amazon']
    invalid_path_dating = ['okcupid']
    invalid_paths = invalid_path_video + invalid_path_image + invalid_path_sound + invalid_path_social_network + \
        invalid_path_aggregator + invalid_path_store + invalid_path_dating
    invalid_paths_regex = re.compile('(' + '|'.join(invalid_paths) + ')')
    return invalid_paths_regex


def _scrap(disconnected):
    invalid_paths_regex = _get_invalid_regex()
    invalid_extensions = ['.jpg', '.gif', '.png', '.webm']
    links_elts = reddit_link_elements_generator(disconnected)
    filtered_links = (link for link in links_elts if _is_valid_link(link, invalid_paths_regex, invalid_extensions))
    docs = _get_doc_generator(filtered_links)
    return docs


def _get_doc_generator(link_elts):
    html_extractor = _HtmlExtractor()
    links_and_htmls = ((link, html_extractor.try_get_html(link.url)) for link in link_elts)
    documents = (Document(link, html) for link, html in links_and_htmls if html is not None)
    return documents


class Scraper(object):

    def __init__(self, disconnected=False):
        self.disconnected = disconnected

    def scrap(self):
        """
        :return: generator of scraperstructs.Document
        """
        return _scrap(self.disconnected)
