

class LinkElement(object):
    def __init__(self, url, origin, origin_title, origin_category, origin_url, origin_id,origin_category_id, date_utc_timestamp):
        self.url = url
        self.origin = origin
        self.origin_title = origin_title
        self.origin_category = origin_category
        self.origin_url = origin_url
        self.origin_id = origin_id
        self.origin_category_id = origin_category_id
        self.date_utc_timestamp = date_utc_timestamp