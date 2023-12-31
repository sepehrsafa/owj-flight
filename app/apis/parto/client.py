# -*- coding: utf-8 -*-
from apps.flights.services.apis.base.client import BaseClient
from ..base.decorators import lazy_property
from .config import Config
from .methods._airLowFareSearchAsync import AirLowFareSearchAsync
from .methods._airRevalidate import AirRevalidate
from .methods._airBook import AirBook
from .methods._airBookingData import AirBookingData
from datetime import datetime, timedelta
import logging
import uuid
from .exceptions import PartoInvalidSessionException
from django.utils import timezone
from apps.flights.choices import SaleStatusChoices
from django_q.tasks import schedule

logger = logging.getLogger(__name__)

class Client(BaseClient):

    __name__ = 'Parto Client'

    @staticmethod
    def support_roundtrip():
        return False

    @staticmethod
    def support_city_search():
        return True

    def _get_flight_search_cache_key(self, origin: str, destination: str, adult_count: int, child_count: int, infant_count: int, departure_date: 'datetime.date',return_date: 'datetime.date', currency: 'CurrencyTypeChoices'):
        if return_date:
            return False
        return f'{self.config._system_code}:{self.config.agency_api_id}:null:{origin}:{destination}:{departure_date}:{return_date}:{adult_count}:{child_count}:{infant_count}:null'



    def _login(self, force_login=False):

        logger.log(logging.DEBUG, 'Login to Parto')

        current_session = self.get_api_session_data()

        if current_session and not force_login:
            logger.log(logging.DEBUG, 'Session is valid')

            self.config.session_id = current_session
            self.touch_api_session_data()

        else:
            logger.log(logging.DEBUG, 'Session is not valid')

            data = {
                'OfficeId': self.config.username.split(':')[0],
                'UserName': self.config.username.split(':')[1],
                'Password': self.config.password,
                'ApplicationId': 'null'
            }

            res = self.config.post('Rest/Authenticate/CreateSession', data=data,add_session_id=False)
            session_id = res.get('SessionId')
            self.config.session_id = session_id
            self.set_api_session_data(session_id)

    def _search_oneway(self, origin, destination, adult_count, child_count, infant_count, departure_date, currency):
        self._login()
        try:
            data = AirLowFareSearchAsync(self).search_oneway(origin, destination, adult_count, child_count, infant_count, departure_date)
        except PartoInvalidSessionException as e:
            self._login(True)
            data = AirLowFareSearchAsync(self).search_oneway(origin, destination, adult_count, child_count, infant_count, departure_date)
        


        return data

    def search_roundtrip(self, origin, destination, adult_count, child_count, infant_count, departure_date, return_date, currency, group_id):
        return None

    @lazy_property
    def fare(self):
        pass

    def _validate(self, offer, fare):
        logger.debug(msg='Validating fare')
        self._login()
        fare_source_code = fare.source.api_details
        try:
            data = AirRevalidate(self).revalidate(fare_source_code)
        except PartoInvalidSessionException as e:
            self._login(True)
            data = AirRevalidate(self).revalidate(fare_source_code)        
        return data

    def fare_rules(fare_id):
        pass

    def fare_baggage(fare_id):
        pass

    def captcha(fare_id):
        pass

    #create a function to turn string in 2023-01-22T01:23:09.2467796+03:30 to datetime
    def _convert_string_to_datetime(self, string):

        index_of_plus = string.index('+')

        string =  string[:index_of_plus-1] + string[index_of_plus:]
        return datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%f%z')


    def _update_booking(self,flight_sale):
        logger.debug(msg='Updating booking')
        self._login()
        AirBookingData(self).update_booking(flight_sale)




    def book(self, flight, passengers, email, phone_number, user, agency, shared_api):
        logger.debug(msg='Booking flight')

        if(flight.fares[0].instant_ticketing_required==True):
            logger.debug(msg='Flight need to be issued immediately')
            ticket_time_limit = timezone.now()
            pnr = None
            status = SaleStatusChoices.NOT_BOOKED_PAYMENT_REQUIRED
            return flight.create_db_record(passengers, pnr, email, phone_number, user, agency, shared_api, {'reserve_data': None}, ticket_time_limit,pnr, status)
        
        else:

            self._login()

            fare_source_code = flight.fares[0].source.api_details

            data = AirBook(self).reserve(fare_source_code, passengers, email, phone_number)
            logger.debug(msg='Booking flight response: %s' % data)
            pnr = data['UniqueId']
            if(data['TktTimeLimit']):
                ticket_time_limit = self._convert_string_to_datetime(data['TktTimeLimit'])
            else:
                ticket_time_limit = timezone.now()
        

            flight_sale =  flight.create_db_record(passengers, pnr, email, phone_number, user, agency, shared_api, {'reserve_data': data},ticket_time_limit,pnr)
            q_data = schedule(
                'apps.flights.services.apis.parto.async.update_booking',
                flight_sale.id,
                shared_api.id,
                schedule_type='O',
                next_run=timezone.now()+timedelta(minutes=1),
                q_options={'timeout': 30, 'broker_name': 'flight_search'}
            )

            logger.log(logging.DEBUG, f"async search called {q_data}")


            return flight_sale

    def issue(self, flight_sale):
        pass

    def __init__(self, config):
        self.config = config
