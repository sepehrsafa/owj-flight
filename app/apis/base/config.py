from abc import ABC, abstractmethod


class BaseConfig(ABC):
    """An Abstract class used to define the general structure of Config class.
    """

    def __init__(self, id, url, key, secret, extra, search_cache_time, search_timeout):
        self.id = id
        self.url = url
        self.key = key
        self.secret = secret
        self.extra = extra
        self.search_cache_time = search_cache_time
        self.search_timeout = search_timeout

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def post(self):
        pass
