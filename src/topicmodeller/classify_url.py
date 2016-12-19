import os
from topicmodeller.topicmodeller import TopicModeller
from scraper.scraper import _HtmlExtractor


def classify_url():
    directory = os.path.dirname(os.path.abspath(__file__))
    root_dir = directory + '/../..'
    topic_model_directory = root_dir + '/docker_images/gator_deps/trained_topic_model'

    topic_modeller = TopicModeller.make_with_html_tokenizer()
    topic_modeller.load(topic_model_directory)

    url = u'https://www.washingtonpost.com/entertainment/books/spanish-author-mendoza-wins-2016-cervantes-literature-prize' \
          u'/2016/11/30/4e51375c-b705-11e6-939c-91749443c5e5_story.html?utm_term=.fa8b7e6b86cc'
    extractor = _HtmlExtractor()
    html = extractor.try_get_html(url)
    is_ok, _ = topic_modeller.classify(html)
    print str(is_ok)


classify_url()
