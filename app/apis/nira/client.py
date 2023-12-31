import logging

from django.utils import timezone

from apps.flights.services.apis.base.client import BaseClient

from ..base.decorators import lazy_property
from .config import Config
from .methods._availability import Availability
from .methods._et_issue import ETIssue
from .methods._fare import Fare
from .methods._reserve import Reserve
from .methods._rt import RT

logger = logging.getLogger(__name__)


class Client(BaseClient):

    __name__ = 'Client'

    @staticmethod
    def support_roundtrip():
        return False

    @staticmethod
    def support_city_search():
        return False


    def _get_flight_search_cache_key(self, origin: str, destination: str, adult_count: int, child_count: int, infant_count: int, departure_date: 'datetime.date',return_date: 'datetime.date', currency: 'CurrencyTypeChoices'):
        #cuz doesn't support roundtrip
        if return_date:
            return False
        return f'{self.config._system_code}:null:{self.config.airline}:{origin}:{destination}:{departure_date}:null:null:null:null:null'


    def _search_oneway(self, origin, destination, adult_count, child_count, infant_count, departure_date, currency):
        data = Availability(self).search(origin, destination, adult_count, child_count, infant_count, departure_date)
        return data

    def search_roundtrip(self, origin, destination, adult_count, child_count, infant_count, departure_date, return_date, currency):
        return None

    @lazy_property
    def fare(self):
        return Fare(self)

    def _validate(self, offer, fare):

        adult_count = 0
        child_count = 0
        infant_count = 0

        for pax in fare.per_pax_breakdown:
            if pax.pax_type == 'ADULT':
                adult_count += pax.number_of_pax
            elif pax.pax_type == 'CHILD':
                child_count += pax.number_of_pax
            elif pax.pax_type == 'INFANT':
                infant_count += pax.number_of_pax

        new_offers = Availability(self).search(
            offer.itineraries[0].segments[0].departure.iata_code, 
            offer.itineraries[0].segments[0].arrival.iata_code, 
            adult_count, 
            child_count, 
            infant_count, 
            offer.itineraries[0].segments[0].departure.at, 
        )

        
        
        founded_new_offer = None 
        for new_offer in new_offers:
            if new_offer.key == offer.key:
                founded_new_offer = new_offer
                break

        if founded_new_offer:
            for new_fare in founded_new_offer.fares:
                if new_fare.per_pax_breakdown[0].details_per_segment[0].fare_basis == fare.per_pax_breakdown[0].details_per_segment[0].fare_basis:
                    founded_new_offer.set_fare(new_fare)
                    return founded_new_offer

        return founded_new_offer


    def fare_rules(fare_id):
        pass

    def fare_baggage(fare_id):
        pass

    def captcha(fare_id):
        pass

    def book(self, flight, passengers, email, phone_number, user, agency, shared_api):
        data = Reserve(self).reserve(
            flight, flight.fares[0], passengers, email, phone_number)
        pnr = data['PNR']
        if not pnr:
            return None

        rt_class = RT(self)
        rt_data = rt_class.rt(pnr=pnr, complete=True)
        rt_class.update_flight(flight, rt_data)
        rt_class.update_fare(flight.fares[0], rt_data)
        return flight.create_db_record(passengers, pnr, email, phone_number, user, agency, shared_api, {'reserve_data': data, 'rt_data': rt_data},timezone.now())

    def issue(self, flight_sale):
        data = ETIssue(self).issue(flight_sale.pnr, flight_sale.email)
        return 0

    def __init__(self, config):
        self.config = config
