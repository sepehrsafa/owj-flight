
import concurrent
import datetime
import logging
from apps.flights.services.apis.nira.exceptions import NiraException
from apps.flights.choices import *
from apps.finance.choices import CurrencyTypeChoices
from apps.accounts.choices import DocumentTypeChoices
from apps.flights.services.search.flight_offer import *
from decimal import Decimal
from .maps import PaxTypeChoicesMap, GenderTypeChoicesMap, TitleTypeChoicesMap
logger = logging.getLogger(__name__)


class AirBookingData:
    method_name = 'Rest/Air/AirBookingData'

    def __init__(self, client):
        self.client = client
        self.config = client.config

    @staticmethod
    def datetime_to_string(data):
        '''
        Convert date and time from string to datetime object
        '''
        return data.strftime('%Y-%m-%dT00:00:00')


    def get_booking_data(self, parto_reference):

        data = {
            "UniqueId": parto_reference
        }
        data = self.config.post(self.method_name, data=data)
        
        return data

    def _update_booking(self, flight_sale, data):
        reservation_items=data['TravelItinerary']['ItineraryInfo']['ReservationItems']

        flight_sale.pnr = reservation_items[0]['AirlinePnr']

        flight_sale.save()

    def update_booking(self, flight_sale):

        data = self.get_booking_data(flight_sale.external_reference)

        if data.get('Success') == True:
            logger.debug(msg='Update booking for flight sale: %s' % flight_sale.id)
            self._update_booking(flight_sale, data)
        else:
            logger.debug(msg='Failed to update booking for flight sale: %s' % flight_sale.id)



