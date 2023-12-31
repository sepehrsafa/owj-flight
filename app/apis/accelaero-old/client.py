# -*- coding: utf-8 -*-
from apps.flights.services.apis.base.client import BaseClient
from ..base.decorators import lazy_property
from .config import Config
from .methods._getAvailability import getAvailability
from .methods._botLogin import Login
from .methods._botFareQuote import FareQuote
from .methods._botBook import Book
from django.utils import timezone


class Client(BaseClient):

    __name__ = 'Client'

    @staticmethod
    def support_roundtrip():
        return False

    @staticmethod
    def support_city_search():
        return False

    def _get_flight_search_cache_key(self, origin: str, destination: str, adult_count: int, child_count: int, infant_count: int, departure_date: 'datetime.date',return_date: 'datetime.date', currency: 'CurrencyTypeChoices'):
        if return_date:
            return False
        return f'{self.config._system_code}:null:{self.config.airline}:{origin}:{destination}:{departure_date}:{return_date}:{adult_count}:{child_count}:{infant_count}:null'


    def _search_oneway(self, origin, destination, adult_count, child_count, infant_count, departure_date, currency):

        data = getAvailability(self).search(origin, destination, adult_count, child_count, infant_count, departure_date)
        return data

    def search_roundtrip(self, origin, destination, adult_count, child_count, infant_count, departure_date, return_date, currency):
        return None

    def _validate(self, offer, fare):

        logins = Login(self).login()

        fare.source.api_details

        fareQuote = FareQuote(self).quote(fare.source.api_details)


        return fareQuote

    def fare_rules(fare_id):
        pass

    def fare_baggage(fare_id):
        pass

    def captcha(fare_id):
        pass

    def book(self, flight, passengers, email, phone_number, user, agency, shared_api):

        login = Login(self).login()
        quoted_fare = FareQuote(self).quote(flight.fares[0].source.api_details)

        #check if quoted_fare has the same price as flight.fares[0]

        book = Book(self).book(flight, flight.fares[0], passengers, email, phone_number)


        pnr = '3232323333'
        if not pnr:
            return None

        return flight.create_db_record(passengers, pnr, email, phone_number, user, agency, shared_api, {'reserve_data': None, 'rt_data': None},timezone.now())

    def issue(self, flight_sale):
        data = ETIssue(self).issue(flight_sale.pnr, flight_sale.email)
        return 0

    def __init__(self, config):
        self.config = config
