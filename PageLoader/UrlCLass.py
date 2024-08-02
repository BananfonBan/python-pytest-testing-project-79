from urllib.parse import urlparse
from urllib.parse import parse_qs


class Url():
    def __init__(self, HTTP):
        self.http = urlparse(HTTP)

    def get_scheme(self):
        return self.http.scheme

    def get_hostname(self):
        return self.http.hostname

    def get_path(self):
        return self.http.path

    def get_query_params(self):
        return parse_qs(self.http.query)

    def get_query_param(self, param, default=None):
        return parse_qs(self.http.query).get(param, [default])[0]

    def __eq__(self, other):
        return self.http == other.http
