# -*- coding: utf-8 -*-

class Document(object):

    def __init__(self, link_element, html_content):
        """
        :param link_element: LinkElement
        :param html_content: string
        """
        self.link_element = link_element
        self.html_content = html_content


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
