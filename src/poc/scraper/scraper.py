from functools import partial
from itertools import ifilter, imap, starmap
import datetime
from reddit import reddit_link_elements_generator
import re
import os
import urllib2
import jsonpickle

def _is_valid_link(link_element, invalid_paths_regex, invalid_extensions):
    path = link_element.url
    extension = os.path.splitext(path)[1]  # splitext split in two : path and extension
    if extension in invalid_extensions:
        return False
    invalid_path_found = invalid_paths_regex.search(path)
    if invalid_path_found:
        return False
    return True

def _try_get_html(url):
    try:
        return urllib2.urlopen(url).read()
    except:
        return None

class Document(object):
    def __init__(self, link_element, html_content):
        self.link_element = link_element
        self.html_content = html_content

def run_scraper(destination_folder):
    invalid_path_video = ['youtu', 'vimeo', 'vid.me', 'tube', 'gfycat', 'vine', 'motion', 'twitch', 'stream', 'video']
    invalid_path_image = ['img', 'flickr', 'flic.kr', 'instagram', 'image', 'imgreview', 'screencloud', 'prnt']
    invalid_path_sound = ['itune', 'soundcloud', 'gifsound', 'spotify']
    invalid_path_social_network = ['twitter', 'facebook']
    invalid_path_aggregator = ['reddit', 'redd.it', 'tumblr', 'voat']
    invalid_path_store = ['ebay', 'amazon']
    invalid_path_dating = ['okcupid']

    invalid_paths = invalid_path_video + invalid_path_image + invalid_path_sound + invalid_path_social_network + \
        invalid_path_aggregator + invalid_path_store + invalid_path_dating

    invalid_extensions = ['.jpg', '.gif', '.png']

    invalid_paths_regex = re.compile('(' + '|'.join(invalid_paths) + ')')

    filter_func = partial(_is_valid_link, invalid_paths_regex=invalid_paths_regex, invalid_extensions=invalid_extensions)
    links_elts = reddit_link_elements_generator()
    filtered_links = ifilter(filter_func, links_elts)
    links_and_htmls = imap( lambda link: (link, _try_get_html(link.url)) , filtered_links)
    filtered_links_html = ifilter(lambda (link, html): html is not None, links_and_htmls)#take only successfully loaded html
    documents = starmap(Document, filtered_links_html)
    docs_as_jsons = imap(jsonpickle.encode, documents)

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    current_date = datetime.datetime.utcnow()
    current_index = 0

    for json_doc in docs_as_jsons:
        with open(destination_folder + '/' + str(current_date) + '_' + str(current_index) + '.json' , 'w') as dest_file:
            dest_file.write(json_doc)
            current_index += 1

