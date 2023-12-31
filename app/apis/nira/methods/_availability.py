
import concurrent
import datetime
import logging
from apps.flights.services.apis.nira.exceptions import NiraException
from apps.flights.choices import *
from apps.accounts.choices import PaxTypeChoices

from apps.finance.choices import CurrencyTypeChoices
from apps.flights.services.search.flight_offer import *
from decimal import Decimal
logger = logging.getLogger(__name__)


class Availability:
    method_name = 'AvailabilityJS.jsp'


    def __init__(self, client):
        self.client = client
        self.config = client.config
        self.airline = self.config.airline
        #self.default_luggage = Luggage(self.config.default_luggage)
        self.business_classes = self.config.business_classes
        self.restricted_classes = self.config.restricted_classes
        self.for_which_nationalities_is_sale_restricted = self.config.for_which_nationalities_is_sale_restricted
        self._flights = []

    def get_class_type(self,name):
        '''
        returns class type based on name
        '''
        if self.business_classes:
            if name[0] in self.business_classes:
                return CabinTypeChoices.BUSINESS
        return CabinTypeChoices.ECONOMY

    @staticmethod
    def date_time_convertor(data):
        '''
        Convert date and time from string to datetime object
        '''
        return datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S').replace(tzinfo=None)

    @staticmethod
    def string_to_date(data):
        return data.strftime('%Y-%m-%d')

    @staticmethod
    def available_classes(data, number_of_pax):
        '''
        returns available classes for each flight based on number of pax and flight class
        '''
        # Sample
        #"/YA I5 S5 R5 O5 V5 B5 Q5 P5 N5 M5 L5 F5 A5 E5 D5 K8 W6 H5 J2 UC XC"

        # REMOVING THE '/' and spliting on spaces and making a list
        data = data[1:].split()
        available_classes = {}

        for flight_class in data:
            # last word inside the str (WX LX MX OX RX BX DX EX SX TX GX) here would be X for all of them
            number_of_seats = flight_class[-1]
            class_name = flight_class[:-1]

            if (number_of_seats == 'X') or (number_of_seats == 'C'):
                continue
            # if the last chr is 'A' in means more than 9 is available
            if number_of_seats == 'A':
                available_classes[class_name] = 9
            # IF NUMBER THEN CHECKING TO SEE IF THERE IS ENOUGH CAPACITY
            elif int(number_of_seats) >= (number_of_pax):
                available_classes[class_name] = int(number_of_seats)

        return available_classes

    @staticmethod
    def taxes(system_fare, tax_string):
        '''
        adds taxes to system fare based on tax string
        '''
        #"I6:30000.0,EN_Desc:PASSENGER SAFETY OVERSIGHT SERVICE,FA_Desc:PASSENGER SAFETY OVERSIGHT SERVICE$HL:10000.0,EN_Desc:HELAL AHMAR TAX,FA_Desc:عوارض هلال احمر$LP:70000.0,EN_Desc:AIRPORT TAX,FA_Desc:فرودگاهي$"
        taxes = tax_string.split('$')
        for tax in taxes:
            if tax:
                tax_info = tax.split(',')
                system_fare.add_tax(
                    Tax(
                        amount=Decimal(tax_info[0].split(':')[1]),
                        code=tax_info[0].split(':')[0],
                        name=tax_info[1].split(':')[1],
                        text=tax_info[1].split(':')[1] +
                        " - " + tax_info[2].split(':')[1]
                    )
                )

    @staticmethod
    def rules(fare, rules_string):
        '''
        adds rules to fare based on rules string
        '''

        fare.add_rule(Rule(
            language="fa",
            details=[x for x in rules_string.replace(
                ",", " ").split('P/') if x],
            name="Cancellation Policy - حالت کنسلی",
            code="CANCELATION_POLICY"
        ))

    @staticmethod
    def is_refundable(data):

        '''
        returns a dict with flight classes as keys and refundability as boolen values
        '''

        data_dict = {}
        start_index = 0
        i = 0
        while i < len(data):
            if data[i] == ':':
                name = data[start_index:i]
                if data[i+1] == 'R':
                    data_dict[name] = True
                    i = i + 12
                    start_index = i
                    continue
                elif data[i+1] == '-':
                    data_dict[name] = False
                    i = i+3
                    start_index = i
                    continue
                elif data[i+1] == 'N':
                    data_dict[name] = False
                    i = i+16
                    start_index = i
                    continue
            i = i+1

        return data_dict

    def fares(self, offer, classes, refundability, adult_count, child_count, infant_count, origin, destination, segment_key):
        '''
        adds fares for each flight offer based on classes, refundability, adult_count, child_count, infant_count, origin, destination
        '''

        with concurrent.futures.ThreadPoolExecutor() as executor:
            fare_infos = {executor.submit(self.client.fare.get_rule, origin,
                                          destination, flight_class): flight_class for flight_class in classes}

            for counter, fare_info_future in enumerate(concurrent.futures.as_completed(fare_infos)):

                fare_info = fare_info_future.result()

                flight_class = fare_info.get('flight_class')

                fare = Fare(FareTypeChoices.PUBLIC,
                            is_refundable=refundability.get(
                                fare_info.get('flight_class')),
                            is_exchangeable=refundability.get(
                                fare_info.get('flight_class')),
                            number_of_bookable_seats=int(
                                classes.get(fare_info.get('flight_class'))),
                            validating_airline=self.airline,
                            restricted_nationalities=self.for_which_nationalities_is_sale_restricted,
                            source=Source(self.config._system_id)
                            )

                if len(self.restricted_classes) == 0:
                    fare.type_of_restriction = TypeOfRestriction.NO_RESTRICTION

                elif flight_class in self.restricted_classes:
                    fare.type_of_restriction = TypeOfRestriction.SALE_NOT_ALLOWED_FOR_SPECIFIED_NATIONALITIES
                
                else:
                    fare.type_of_restriction = TypeOfRestriction.SALE_ONLY_ALLOWED_FOR_SPECIFIED_NATIONALITIES
                

                self.rules(fare, fare_info.get('CRCNRules'))

                segment_info = SegmentInfo(
                    segment_id=1,
                    segment_key=segment_key,
                    cabin=self.get_class_type(fare_info.get('flight_class')),
                    fare_basis=fare_info.get('flight_class'),
                    booking_class=fare_info.get('flight_class')[0]
                )
                if adult_count != 0:
                    system_fare = SystemFare(
                        base=Decimal(fare_info.get('AdultFare')),
                        total=Decimal(fare_info.get('AdultTotalPrice')),
                        currency=CurrencyTypeChoices.IRR
                    )
                    self.taxes(system_fare, fare_info.get('AdultTaxes'))
                    fare.add_pax_info(
                        PaxInfo(
                            PaxTypeChoices.ADULT,
                            system_fare=system_fare,
                            number_of_pax=adult_count,
                            details_per_segment=[segment_info]
                        )
                    )

                if child_count != 0:
                    system_fare = SystemFare(
                        base=Decimal(fare_info.get('ChildFare')),
                        total=Decimal(fare_info.get('ChildTotalPrice')),
                        currency=CurrencyTypeChoices.IRR
                    )
                    self.taxes(system_fare, fare_info.get('ChildTaxes'))
                    fare.add_pax_info(
                        PaxInfo(
                            PaxTypeChoices.CHILD,
                            system_fare=system_fare,
                            number_of_pax=child_count,
                            details_per_segment=[segment_info]
                        )
                    )
                if infant_count != 0:
                    system_fare = SystemFare(
                        base=Decimal(fare_info.get('InfantFare')),
                        total=Decimal(fare_info.get('InfantTotalPrice')),
                        currency=CurrencyTypeChoices.IRR
                    )
                    self.taxes(system_fare, fare_info.get('InfantTaxes'))
                    fare.add_pax_info(
                        PaxInfo(
                            PaxTypeChoices.INFANT,
                            system_fare=system_fare,
                            number_of_pax=infant_count,
                            details_per_segment=[segment_info]
                        )
                    )

                offer.add_fare(fare)

    def search(self, origin, destination, adult_count, child_count, infant_count, departure_date):
        '''
        returns a list of offer objects based on origin, destination, adult_count, child_count, infant_count, departure_date
        if any errors, returns None
        '''
        
        params = {
            'cbSource': origin,
            'cbTarget': destination,
            'DepartureDate': self.string_to_date(departure_date),
        }

        logger.debug(f'Nira flight search params: {self.airline} {origin} {destination} {adult_count} {child_count} {infant_count} {departure_date}')

        # MAKING GET REQUEST FOR AVAIL FLIGHTS

        try:
            data = self.config.get(method=self.method_name, data=params)
        except Exception as e:
            logger.error(msg=e)
            return []

        # CHEACKING THE API RESPONSE
        for flight in data['AvailableFlights']:

            classes = self.available_classes(
                flight['ClassesStatus'], adult_count+child_count)

            if not classes:
                continue

            offer = Offer()

            itinerary = Itinerary(1)

            departure_location = Location(
                iata_code=flight.get('Origin'),
                terminal=None,
                at=self.date_time_convertor(flight.get('DepartureDateTime')),
            )

            arrival_location = Location(
                iata_code=flight.get('Destination'),
                terminal=None,
                at=self.date_time_convertor(flight.get('ArrivalDateTime')),
            )

            itinerary.add_segment(Segment(
                segment_id=1,
                departure=departure_location,
                arrival=arrival_location,
                flight_number=str(flight.get('FlightNo')),
                operating_flight_number=str(flight.get('OperatingFlightNo')),
                marketing_airline=flight.get('Airline'),
                operating_airline=flight.get('OperatingAirline'),
                equipment=flight.get('AircraftTypeCode'),
            ))
            if flight.get('Transit'):
                segment.add_stop(Stop(None, None, None, None, None))
            segment_key = itinerary.segments[0].segment_key
            offer.add_itinerary(itinerary)
            refundability = self.is_refundable(flight.get('ClassRefundStatus'))
            self.fares(offer, classes, refundability, adult_count, child_count,
                       infant_count, origin, destination, segment_key)
            self._flights.append(offer)

        return self._flights
