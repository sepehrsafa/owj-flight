
import datetime
import logging
from apps.flights.choices import *
from apps.finance.choices import CurrencyTypeChoices
from apps.flights.services.search.flight_offer import *
from apps.accounts.choices import PaxTypeChoices
from .maps import PaxTypeChoicesMap
from xml.etree import ElementTree
from decimal import Decimal
from ..datatypes import AccelAeroFlightRPH
logger = logging.getLogger(__name__)


class GetPrice:
    method_name = 'GetPrice'
    BASE_SCHEMA_URL = '{http://www.opentravel.org/OTA/2003/05}'
    def __init__(self, client):
        self.client = client
        self.config = client.config
        self.airline = self.config.airline
        self.booking_chanel = self.config.booking_chanel
        self.username = self.config.username
        self.requestor_id_type = self.config.requestor_id_type
        self.terminal_id = self.config.terminal_id
        self.BASE_SCHEMA_URL = '{http://www.opentravel.org/OTA/2003/05}'
        self.flight_refs = []

    @staticmethod
    def string_to_datetime(data):
        '''
        Convert date and time from string to datetime object
        '''
        return datetime.datetime.strptime(data, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=None)

    @staticmethod
    def datetime_date_to_string(data):
        "given a datetime object it will return string data in following format %Y-%m-%d - 2022-11-07"
        return data.strftime('%Y-%m-%d')


    
    def create_flight(self, itineraries):
        return_itineraries = []
        for itinerary_id, itinerary_xml in enumerate(itineraries):
            itinerary = Itinerary(itinerary_id+1)
            segments = itinerary_xml.findall(f".//{GetPrice.BASE_SCHEMA_URL}FlightSegment")
            for segment_id, segment in enumerate(segments):
                departure_airport = segment.find(f"{GetPrice.BASE_SCHEMA_URL}DepartureAirport").attrib
                arrival_airport = segment.find(f"{GetPrice.BASE_SCHEMA_URL}ArrivalAirport").attrib
                segment_details = segment.attrib

                self.flight_refs.append(AccelAeroFlightRPH(segment_details.get('RPH')))

                flight_ref = segment_details.get('RPH').split('$')

                departure_location = Location(
                    iata_code=departure_airport.get('LocationCode'),
                    terminal=departure_airport.get('Terminal'),
                    at=self.string_to_datetime(segment_details.get('DepartureDateTime')),
                )

                arrival_location = Location(
                    iata_code=arrival_airport.get('LocationCode'),
                    terminal=arrival_airport.get('Terminal'),
                    at=self.string_to_datetime(segment_details.get('ArrivalDateTime')),
                )
                flight_segment = Segment(
                    segment_id=itinerary_id+segment_id+1,
                    departure=departure_location,
                    arrival=arrival_location,
                    flight_number=segment_details.get('FlightNumber')[2:],
                    operating_flight_number=segment_details.get('FlightNumber')[2:],
                    marketing_airline=segment_details.get('FlightNumber')[:2],
                    operating_airline=segment_details.get('FlightNumber')[:2],
                    equipment=None,
                )

                if(segment_details.get('StopQuantity')):
                    segment_code = flight_ref[1].split('/')
                    if int(segment_details.get('StopQuantity')) == (len(segment_code)-2):
                        for i in range(int(segment_details.get('StopQuantity'))):
                            flight_segment.add_stop(Stop(segment_code[i+1]))

                itinerary.add_segment(flight_segment)
            return_itineraries.append(itinerary)
        return return_itineraries
        
        
    
    def create_fare(self, ptc_fare_break_downs, source_info):
        fare = Fare(
            FareTypeChoices.PUBLIC,
            is_refundable=None,
            is_exchangeable=None,
            number_of_bookable_seats=None,
            validating_airline="W5",
        )

        
        for ptc in ptc_fare_break_downs:
            BaseFare = ptc.find(f".//{GetPrice.BASE_SCHEMA_URL}BaseFare").attrib
            TotalFare = ptc.find(f".//{GetPrice.BASE_SCHEMA_URL}TotalFare").attrib
            PassengerTypeQuantity = ptc.find(f".//{GetPrice.BASE_SCHEMA_URL}PassengerTypeQuantity").attrib
            taxes = ptc.findall(f".//{GetPrice.BASE_SCHEMA_URL}Tax")
            fees = ptc.findall(f".//{GetPrice.BASE_SCHEMA_URL}Fee")
            fare_infos = ptc.findall(f".//{GetPrice.BASE_SCHEMA_URL}FareInfo")

            system_fare = SystemFare(
                base=Decimal(BaseFare.get('Amount')),
                total=Decimal(TotalFare.get('Amount')),
                currency=CurrencyTypeChoices.IRR
            )
            for tax in taxes:
                tax_json = tax.attrib
                system_fare.add_tax(
                    Tax(
                            amount=Decimal(tax_json.get('Amount')),
                            code=tax_json.get('TaxCode'),
                            name=tax_json.get('TaxName'),
                    )
                )
            for fee in fees:
                fee_json = fee.attrib
                system_fare.add_fee(
                    Fee(
                            amount=Decimal(fee_json.get('Amount')),
                            code=fee_json.get('FeeCode'),
                            name=fee_json.get('FeeName'),
                    )
                )


            pax_info = PaxInfo(
                pax_type=PaxTypeChoicesMap.get(PassengerTypeQuantity.get('Code')),
                system_fare=system_fare,
                number_of_pax=int(PassengerTypeQuantity.get('Quantity')),
            )

            for fare_info_count,fare_info in enumerate(fare_infos):
                fare_info_json = fare_info.attrib
                
                pax_info.add_segment_info(
                    SegmentInfo(
                        segment_id=fare_info_count+1,
                        segment_key=fare_info_json.get('SegmentCode'),
                        cabin=CabinTypeChoices.ECONOMY,
                        fare_basis=fare_info_json.get('FareRuleInfo'),
                        booking_class=fare_info_json.get('FareBasisCode')
                    )
                )
                fare_info_rule = fare_info.find(f".//{GetPrice.BASE_SCHEMA_URL}FareRuleReference")
                fare.add_rule(
                    Rule(
                        name="GENERAL",
                        language = "EN", 
                        details = fare_info_rule.text.split(";"),
                        segment_code=fare_info_json.get('SegmentCode')
                    )
                )
            fare.add_pax_info(pax_info)
        source_info.flight_refs = self.flight_refs
        fare.set_source(Source(system_id=self.config._system_code,api_details=source_info))
        return fare


    def create_offer(self, priced_itinerary, source_info):
        
        itineraries = priced_itinerary.findall(f".//{GetPrice.BASE_SCHEMA_URL}OriginDestinationOption")
        ptc_fare_breakdowns = priced_itinerary.findall(f".//{GetPrice.BASE_SCHEMA_URL}PTC_FareBreakdown")
        
        offer = Offer( 
            itineraries= self.create_flight(itineraries),
        )
        offer.add_fare(self.create_fare(ptc_fare_breakdowns,source_info))
        self.flight_refs = []
        return offer


        

    def xml_quote(self,xml_origin_destination_options, transaction_identifier, adult_count, child_count, infant_count, offer_type, source_info):
        if 'ONE_WAY' in offer_type:
            direction_ind = "OneWay"
        else:
            direction_ind = "Return"

        self.adult_count = adult_count
        self.child_count = child_count
        self.infant_count = infant_count

        xml_origin_destination_options_str = ElementTree.tostring(xml_origin_destination_options)
        request_data = f"""
        <ns:OTA_AirPriceRQ Target="Production" TransactionIdentifier="{transaction_identifier}" Version="20061.00">
            <ns:POS>
                <ns:Source TerminalID="{self.terminal_id}">
                    <ns:RequestorID Type="{self.requestor_id_type}" ID="{self.username}" />
                    <ns:BookingChannel Type="{self.booking_chanel}" />
                </ns:Source>
            </ns:POS>
            <ns:AirItinerary  DirectionInd="{direction_ind}">
                {xml_origin_destination_options_str}
            </ns:AirItinerary>
            <ns:TravelerInfoSummary>
                <ns:AirTravelerAvail>
                    <ns:PassengerTypeQuantity Code="ADT" Quantity="{adult_count}"/>
                    <ns:PassengerTypeQuantity Code="CHD" Quantity="{child_count}"/>
                    <ns:PassengerTypeQuantity Code="INF" Quantity="{infant_count}"/>
                </ns:AirTravelerAvail>
            </ns:TravelerInfoSummary>
        </ns:OTA_AirPriceRQ>
        """
        # MAKING GET REQUEST FOR AVAIL FLIGHTS

        data = self.config.post(data=request_data)

        root = ElementTree.fromstring(data['data'])

        ota_air_price_rs = root[0][0]

        errors = ota_air_price_rs.find(f'{self.BASE_SCHEMA_URL}Errors')

        for error in errors:
            print(error.text, error.attrib)

        quotedItinerary = ota_air_price_rs.find(f".//{self.BASE_SCHEMA_URL}PricedItinerary")
        if quotedItinerary:
            offer = self.create_offer(quotedItinerary,source_info)
            return offer
        else:
            return None

