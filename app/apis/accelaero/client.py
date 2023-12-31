import logging
from ..base import BaseConfig, BaseClient
from app.enums import APIClient
import requests
from app.schemas import FlightGridRequest, FlightSearchRequest
import datetime
from .methods._getAvailability import search


class AccelAeroClient(BaseClient):
    __name__: str = APIClient.ACCELAERO.value + "Client"
    client: APIClient = APIClient.ACCELAERO
    BASE_SCHEMA_URL = "{http://www.opentravel.org/OTA/2003/05}"

    def __init__(self, id, url, key, secret, extra, search_timeout):
        super().__init__(id, url, key, secret, extra, search_timeout)
        self.terminal_id = extra.get("terminal_id")
        self.requestor_id_type = extra.get("requestor_id_type")
        self.booking_chanel = extra.get("booking_chanel")
        self.bot_session = requests.Session()
        self.session = requests.Session()

    def get_search_cache_key(self, request: FlightGridRequest):
        return f"{self.client.value}:{self.id}:{request.departure_date}:{request.return_date}:{request.origin}:{request.destination}:{request.currency}"

    def grid_search(self, request: FlightGridRequest):
        return []

    def search(self, request: FlightSearchRequest):
        return search(self, request)

    def validate(self, offer, fare):
        pass

    def fare_rules(fare_id):
        pass

    def fare_baggage(fare_id):
        pass

    def captcha(fare_id):
        pass

    def book():
        pass

    def issue():
        pass
