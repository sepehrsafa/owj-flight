import datetime
from apps.flights.choices import FareTypeChoices
from apps.finance.choices import CurrencyTypeChoices
from apps.flights.services.search.flight_offer import *
from decimal import Decimal
from .maps import PaxTypeChoicesMap, CabinClassChoicesMap
from ..datatypes import AccelAeroFlightRPH
import json

class FareQuote:
    def __init__(self, client):
        self.client = client
        self.config = client.config
        self.airline = self.config.airline
        self.username = self.config.username
        self.password = self.config.password
        self.airline = None
        self.flight_refs = []


    def _set_to_search(self):

        status, text, headers = self.config.get('xbe/private/makeReservation.action?mc=false')
        if status != 200:
            return False
        return True

    def string_to_datetime(self, data):
        return datetime.datetime.strptime(data, '%y%m%d%H%M')

    def create_offer(self, data: 'flightInfo'):
        offer = Offer()
        for flight_id, flight in enumerate(data):
            itinerary = Itinerary(flight_id+1)

            stop_quantity = flight.get('noOfStops')
            if stop_quantity=='Non-Stop':
                stop_quantity = 0
            else:
                stop_quantity=stop_quantity.lower()
                #replace all combination of stop, stops, Stop, Stop(s) with ''
                try:
                    stop_quantity = int(stop_quantity.replace('stop(s)', '').replace('stop', '').replace('stops', '').replace(' ', ''))
                except:
                    stop_quantity = 0
            

            segment_codes = flight.get('orignNDest').split('/')

            if len(segment_codes)-2 != stop_quantity:
                stop_quantity = len(segment_codes)-2

            stops = []
            for i in range(1, stop_quantity):
                stops.append(
                    Stop(
                        iata_code=segment_codes[i],
                    )
                )
            departure = Location(
                iata_code=flight.get('departure'),
                at=self.string_to_datetime(flight.get('departureDateValue')),
                terminal= flight.get('departureTerminal') if flight.get('departureTerminal') != "-" else None,
            )
            arrival = Location(
                iata_code=flight.get('arrival'),
                at=self.string_to_datetime(flight.get('arrivalDateValue')),
                terminal= flight.get('arrivalTerminal') if flight.get('arrivalTerminal') != "-" else None,
            )
            marketing_airline_code = flight.get('airLine')
            flight_number = flight.get('flightNo').replace(marketing_airline_code, '')
            operating_airline_code = flight.get('airLine')
            operating_airline_flight_number = marketing_airline_code
            operating_airline_flight_number = operating_airline_flight_number.replace(operating_airline_code, '') 
            segment = Segment(
                segment_id=flight_id+1,
                departure=departure,
                arrival=arrival,
                operating_airline=operating_airline_code,
                operating_flight_number=operating_airline_flight_number,
                marketing_airline=marketing_airline_code,
                flight_number=flight_number,
                equipment=flight.get('flightModelDescription'),
                stops=stops,
                stop_quantity=stop_quantity,
                code=flight.get('orignNDest'),
                remarks=flight.get('remarks'),
            )
            itinerary.add_segment(segment)
            offer.add_itinerary(itinerary)
            self.airline = marketing_airline_code

            self.source_info.add_flight_rph(AccelAeroFlightRPH(flight.get('flightRefNumber'),flight.get('departureDateZuluValue')))

        return offer

    def create_fare(self, data: 'availableFare'):
        pax_fare = data.get('paxFareTOs')
        fare_rules = data.get('fareRulesInfo').get('fareRules')
        taxes = data.get('taxTOs')
        surcharges = data.get('surchargeTOs')

        is_charter = False
        segment_info = []
        fare_rules = []
        is_refundable = False

        for fare_rule_id, fare_rule in enumerate(fare_rules):

            segment_info.append(
                SegmentInfo(
                    segment_id=fare_rule_id+1,
                    segment_key=fare_rule.get('orignNDest'),
                    cabin=CabinClassChoicesMap.get(fare_rule.get('cabinClassCode')),
                    booking_class=fare_rule.get('bookingClassCode'),
                    fare_basis=fare_rule.get('fareBasisCode'),
                )
            )
            fare_rules.append(
                Rule(
                    language="EN",
                    details=fare_rule.get('comments').split(";"),
                    name="GENERAL",
                    segment_code=fare_rule.get('orignNDest'),
                )
            )
            is_refundable = fare_rule.get('adultFareRefundable')
                

        fare = Fare(
            fare_type=FareTypeChoices.PUBLIC,
            validating_airline=self.airline,
            is_refundable=is_refundable,
            instant_ticketing_required=data.get('fareQuoteSummaryTO').get('onHoldRestricted'),
            source=Source(system_id=self.config._system_code,api_details=self.source_info)
        )

        for ptc_breakdown in pax_fare:

            pax_type = ptc_breakdown.get('paxType')

            system_fare = SystemFare(
                base=Decimal(ptc_breakdown.get('fare')),
                total=Decimal(ptc_breakdown.get('perPax')),
                taxes=[Tax(Decimal(tax.get('amountInLocalCurrency')),tax.get('taxCode'),tax.get('taxName')) for tax in taxes if tax.get('applicableToDisplay') == pax_type],
                services=[Tax(Decimal(surcharge.get('amountInLocalCurrency')),surcharge.get('taxCode'),surcharge.get('taxName')) for surcharge in surcharges if surcharge.get('applicableToDisplay') == pax_type],
                currency=CurrencyTypeChoices['IRR'],
            )
            print(system_fare)
            fare.add_pax_info(
                PaxInfo(
                    pax_type=PaxTypeChoicesMap.get(pax_type),
                    number_of_pax=int(ptc_breakdown.get('noPax')),
                    system_fare=system_fare,
                    details_per_segment=segment_info
                )
            )
        return fare


    def quote(self,source_info):
        if(not self._set_to_search()):
            return False
        
        self.source_info = source_info.get_copy()
        
        data = {
            'fareQuoteParams.fromAirport': source_info.origin,
            'fareQuoteParams.toAirport': source_info.destination,
            'fareQuoteParams.departureDate': '25/06/2002',
            'fareQuoteParams.returnDate': '',
            'fareQuoteParams.adultCount': source_info.adult_count,
            'fareQuoteParams.childCount': source_info.child_count,
            'fareQuoteParams.infantCount': source_info.infant_count,
            'fareQuoteParams.classOfService': source_info.cabin_of_service,
            'fareQuoteParams.selectedCurrency': 'IRR',
            'fareQuoteParams.bookingType': 'NORMAL',
        }
        for flight_ref_id, flight_ref in enumerate(source_info.flight_refs):
            data[f'outFlightRPHList[{flight_ref_id}]'] = flight_ref.flight_rph
        additional_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f'{self.config.site_url}/xbe/private/makeReservation.action?mc=false'
        }
        status, text, headers = self.config.post_form('xbe/private/loadFareQuote.action', data=data, headers=additional_headers)

        data = json.loads(text)
        offer = self.create_offer(data.get('flightInfo'))
        fare = self.create_fare(data.get('availableFare'))
        offer.add_fare(fare)

        return offer