
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


class AirBook:
    method_name = 'Rest/Air/AirBook'

    def __init__(self, client):
        self.client = client
        self.config = client.config

    @staticmethod
    def datetime_to_string(data):
        '''
        Convert date and time from string to datetime object
        '''
        return data.strftime('%Y-%m-%dT00:00:00')

    def create_travelers(self, passengers):
        '''
        Create list of passengers
        '''
        travelers = []
        for passenger in passengers:
            passenger = passenger.passenger_model
            traveler = {
                "DateOfBirth": self.datetime_to_string(passenger.birth_date),
                "Gender": GenderTypeChoicesMap.to(passenger.gender),
                "PassengerType": PaxTypeChoicesMap.to(passenger.age_group),
                "PassengerName": {
                    "PassengerFirstName": passenger.first_name_english,
                    "PassengerMiddleName": passenger.middle_name_english,
                    "PassengerLastName": passenger.last_name_english,
                    "PassengerTitle": TitleTypeChoicesMap.to(passenger.title)
                },
                "SeatPreference": 0,
                "MealPreference": 0,
                "Wheelchair": False,
                'NationalId': '2833411839'
            }

            if passenger.document_type == DocumentTypeChoices.PASSPORT:
                traveler.update({'Passport': {
                    "Country": passenger.document_issuance_county,
                    "ExpiryDate": self.datetime_to_string(passenger.document_expiry_date),
                    "PassportNumber": passenger.document_number,
                }})
                traveler["nationality"] = passenger.nationality
            elif passenger.document_type == DocumentTypeChoices.IRAN_ID:
                traveler["nationality"] = 'IR'
                traveler['NationalId'] = passenger.document_number

            travelers.append(traveler)

        return travelers

    def reserve(self, fare_source_code, passengers, email, phone_number):

        data = {
            "FareSourceCode": fare_source_code,
            "TravelerInfo": {
                "PhoneNumber": phone_number.as_e164,
                "Email": email,
                "AirTravelers": self.create_travelers(passengers)
            }
        }
        logger.debug(msg=f'AirBook request: {data}')

        dummy_data = {
            "Success": True,
            "Gateway": None,
            "TktTimeLimit": "2018-05-06T13:30:00.0000000+04:30",
            "Category": 10,
            "Status": 10,
            "UniqueId": "PO0000001",
            "Error": None,
            "PayData": {
                "Amount": 68.69,
                "AirQueueId": 1,
                "PayForService": 1
            }
        }
        #data = self.config.post(self.method_name, data=data)

        return dummy_data
