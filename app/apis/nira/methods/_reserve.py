import datetime
import logging
from apps.flights.services.apis.nira.exceptions import NiraException
from apps.flights.choices import *
from apps.finance.choices import CurrencyTypeChoices
from apps.flights.services.search.flight_offer import *
from decimal import Decimal
from django.shortcuts import get_object_or_404
from datetime import date
from apps.accounts.choices import DocumentTypeChoices, GenderTypeChoices

logger = logging.getLogger(__name__)


class Reserve:
    method_name = 'ReservJS'


    def __init__(self, client):
        self.client = client
        self.config = client.config
        self.airline = self.config.airline
        self.default_luggage = Luggage(self.config.default_luggage)
        self.business_classes = self.config.business_classes

    def get_class_type(self,name):
        '''
        returns class type based on name
        '''
        if self.business_classes:
            if name[0] in self.business_classes:
                return CabinTypeChoices.BUSINESS
        return CabinTypeChoices.ECONOMY

    @staticmethod
    def string_to_date(data):
        return data.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_age(birth_date):
        # Get today's date object
        today = date.today()
        
        # A bool that represents if today's day/month precedes the birth day/month
        one_or_zero = ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        # Calculate the difference in years from the date object's components
        year_difference = today.year - birth_date.year
        
        # The difference in years is not enough. 
        # To get it right, subtract 1 or 0 based on if today precedes the 
        # birthdate's month/day.
        
        # To do this, subtract the 'one_or_zero' boolean 
        # from 'year_difference'. (This converts
        # True to 1 and False to 0 under the hood.)
        age = year_difference - one_or_zero
        return age

    @staticmethod
    def get_date(date):
        if date:
            return date.strftime("%d%b%y")
        return ''

    @staticmethod
    def get_title(gender):
        if gender == GenderTypeChoices.M:
            return 'MR'
        elif gender == GenderTypeChoices.F:
            return 'MRS'


    def reserve(self, flight, fare, passengers, email, phone_number):
        data = {
            'Airline': self.airline,
            'cdSource': flight.itineraries[0].segments[0].departure.iata_code,
            'cdTarget': flight.itineraries[0].segments[0].arrival.iata_code,
            'FlightClass' : fare.per_pax_breakdown[0].details_per_segment[0].fare_basis,
            'FlightNo' : flight.itineraries[0].segments[0].flight_number,
            'DepartureDate' : self.string_to_date(flight.itineraries[0].segments[0].departure.at),
            'No': len(passengers),
            'edtContact' : f'{phone_number.as_national.replace(" ", "")}|{email}',
        }
        for i in range(len(passengers)):
            passenger = passengers[i].passenger_model
            data['EdtName'+str(i+1)] = f'{passenger.first_name_english}{self.get_title(passenger.gender)}'
            data['EdtLast'+str(i+1)] = passenger.last_name_english
            data['EdtAge'+str(i+1)] = self.get_age(passenger.birth_date)

            if passenger.document_type == DocumentTypeChoices.PASSPORT:

                data['EdtID'+str(i+1)] = f'P'
            else:
                data['EdtID'+str(i+1)] = f'I'

            data['EdtID'+str(i+1)]+= f'_{passenger.document_issuance_county}_{passenger.document_number}_{passenger.document_issuance_county}_{self.get_date(passenger.birth_date)}_{passenger.gender}_{self.get_date(passenger.document_expiry_date)}_{passenger.last_name_english}_{passenger.first_name_english}'

        print(data)
        res = self.config.post(method=Reserve.method_name, data=data)
        print(res)
        try:
            pnr = res['AirReserve'][0]
        except Exception as e:
            logger.error(f'PNR not found: {e}')
            raise NiraException(res)
        
        return pnr
            
        