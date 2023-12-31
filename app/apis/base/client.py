import logging
from abc import ABC, abstractmethod
from app.enums import APIClient
from app.schemas import FlightGridRequest, FlightSearchRequest


class BaseClient(ABC):
    __name__ = "Client"
    client: APIClient = None

    def __init__(self, id, url, key, secret, extra, search_timeout):
        self.id = id
        self.url = url
        self.key = key
        self.secret = secret
        self.extra = extra
        self.search_timeout = search_timeout
        self.logger = logging.getLogger(self.__name__)

    @abstractmethod
    def get_search_cache_key(self, request: FlightGridRequest):
        pass

    @abstractmethod
    def grid_search(self, request: FlightGridRequest):
        pass

    @abstractmethod
    def search(self, request: FlightSearchRequest):
        pass

    @abstractmethod
    def validate(self, offer, fare):
        pass

    @abstractmethod
    def fare_rules(fare_id):
        pass

    @abstractmethod
    def fare_baggage(fare_id):
        pass

    @abstractmethod
    def captcha(fare_id):
        pass

    @abstractmethod
    def book():
        pass

    @abstractmethod
    def issue():
        pass
