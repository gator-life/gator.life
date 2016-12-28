# -*- coding: utf-8 -*-

import re
import os
import socket
import ssl
import logging
import urlparse
import cchardet
import requests
import lxml
import readability
from .reddit import reddit_link_elements_generator

LOGGER = logging.getLogger(__name__)


class Document(object):

    def __init__(self, url, title, content):
        """
        :param url: Unicode
        :param title: Unicode. Title of the article
        :param content: Unicode. Content of the article (html markup already cleaned)
        """
        self.url = url
        self.title = title
        self.content = content


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

    def try_get_html(self, url):  # pylint: disable=too-many-return-statements
        try:
            LOGGER.debug('get html from url[%s]', url)
            head_response = self._requests.head(url, timeout=0.5)
            if "Content-Type" not in head_response.headers:
                LOGGER.info('filtered: missing Content-Type header, url:%s', url)
                return None
            if not "text/html" in head_response.headers["Content-Type"]:
                LOGGER.info('filtered: not html, url:%s', url)
                return None
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
    invalid_extensions = ['.jpg', '.gif', '.png', '.webm', '.zip']
    links_elts = reddit_link_elements_generator(disconnected)
    filtered_links = (link for link in links_elts if _is_valid_link(link, invalid_paths_regex, invalid_extensions))
    docs = _get_doc_generator(filtered_links)
    return docs


def _get_doc_generator(link_elts):
    html_extractor = _HtmlExtractor()
    for link_elt in link_elts:
        html = html_extractor.try_get_html(link_elt.url)
        if html is None:
            continue
        doc = _try_get_document(link_elt.url, html)
        if doc is None:
            continue
        yield doc


def _try_get_document(url, html):
    readability_doc = readability.Document(html)
    text_without_useless_parts = readability_doc.summary()
    content_without_html_markup = unicode(lxml.html.fromstring(text_without_useless_parts).text_content())
    title = unicode(readability_doc.short_title())
    if content_without_html_markup is None or title is None or content_without_html_markup == u'' or title == u'':
        return None
    return Document(unicode(url), title, content_without_html_markup)


class Scraper(object):

    def __init__(self, disconnected=False):
        self.disconnected = disconnected

    def scrap(self):
        """
        :return: generator of scraperstructs.Document
        """
        return _scrap(self.disconnected)
