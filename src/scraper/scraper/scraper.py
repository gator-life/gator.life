import codecs
import datetime
from time import sleep
import re
import os
import socket
import ssl
import logging
import cchardet
import requests
import urlparse
import jsonpickle

from .reddit import reddit_link_elements_generator
from common.scraperstructs import Document

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


def _try_get_html(url):
    try:
        data = requests.get(url, timeout=2)

        header_encoding = data.encoding
        if not header_encoding:
            return None
        # cchardet way faster than data.apparent_encoding
        # https://github.com/kennethreitz/requests/issues/2359
        guessed_encoding = cchardet.detect(data.content)['encoding'].lower()
        if guessed_encoding is None or header_encoding.lower() != guessed_encoding:
            return None
        data.content.decode(guessed_encoding)  # check we can get unicode object from raw data (could raise exception)
        return data.text
    except (ssl.SSLError, socket.timeout, UnicodeDecodeError, requests.exceptions.RequestException) as expected_exception:
        logging.warning('managed exception, url: ' + url)
        logging.exception(expected_exception)
        return None
    #  to not crash the whole process...
    except Exception as unexpected_exception:  # pylint: disable=broad-except
        logging.error('unexpected exception, url: ' + url)
        logging.exception(unexpected_exception)
        return None


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


def scrap(disconnected=False):
    """
    :return: a generator of Document as json strings, can be deserialized by jsonpickle
    """
    invalid_paths_regex = _get_invalid_regex()
    invalid_extensions = ['.jpg', '.gif', '.png', '.webm']
    links_elts = reddit_link_elements_generator(disconnected)
    filtered_links = (link for link in links_elts if _is_valid_link(link, invalid_paths_regex, invalid_extensions))
    docs_as_jsons = _get_json_doc_generator(filtered_links)
    return docs_as_jsons


def _get_json_doc_generator(link_elts):
    jsonpickle.set_encoder_options('simplejson', indent=4, ensure_ascii=False)  # set unicode and pretty-print

    links_and_htmls = ((link, _try_get_html(link.url)) for link in link_elts)
    documents = (Document(link, html) for link, html in links_and_htmls if html is not None)
    docs_as_jsons = (jsonpickle.encode(d) for d in documents)
    return docs_as_jsons

def _dump_json_docs(docs_as_json, destination_folder):
    current_date = datetime.datetime.utcnow()
    current_index = 0
    for json_doc in docs_as_json:
        filename = destination_folder + '/' + str(current_date) + '_' + str(current_index) + '.json'
        with codecs.open(filename=filename, mode='w', encoding='utf-8') as dest_file:
            dest_file.write(json_doc)
        current_index += 1

def scrap_and_dump(destination_folder):
    """
    scrap and dump one document by file
    :param destination_folder: string of the folder path, folder must already exist
    """
    # we need this high level loop to prevent crash because exceptions are thrown by internal reddit generator
    # a generator cannot be continued after it raises an exception, so we have to make another generator and restart
    # The observed exception was due to a deficient connection. We sleep to not flood logs (it won't come back immediately)
    while True:
        try:
            docs_as_jsons = scrap()
            _dump_json_docs(docs_as_jsons, destination_folder)
        except Exception as exception:  # pylint: disable=broad-except
            logging.error("The scraper crashed! starting it over...")
            logging.exception(exception)
            sleep(30)
            