# Description: This file contains the getAvailability method for the Accelaero API
import datetime
import logging
from xml.etree import ElementTree
from ._getPrice import GetPrice
from ..datatypes import AccelAeroSourceInfo
logger = logging.getLogger(__name__)

class getAvailability:
    method_name = 'getAvailability'

    def __init__(self, client):
        self.client = client
        self.config = client.config
        self.airline = self.config.airline
        self.booking_chanel = self.config.booking_chanel
        self.username = self.config.username
        self.requestor_id_type = self.config.requestor_id_type
        self.terminal_id = self.config.terminal_id
        #self.default_luggage = Luggage(self.config.default_luggage)
        self._flights = []
        self.quotedItineraryRPHs=None
        self.quotedAirItineraryPricingInfo=None
        self.BASE_SCHEMA_URL = '{http://www.opentravel.org/OTA/2003/05}'



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



    def search(self, origin, destination, adult_count, child_count, infant_count, departure_date):
        '''
        returns a list of offer objects based on origin, destination, adult_count, child_count, infant_count, departure_date
        if any errors, returns None
        '''
        
        request_data = f"""
            <ns:OTA_AirAvailRQ Target="Production" Version="2006.01" DirectFlightsOnly="false">
                <ns:POS>
                    <ns:Source TerminalID="{self.terminal_id}">
                        <ns:RequestorID Type="{self.requestor_id_type}" ID="{self.username}" />
                        <ns:BookingChannel Type="{self.booking_chanel}" />
                    </ns:Source>
                </ns:POS>
                <ns:OriginDestinationInformation>
                    <ns:DepartureDateTime>{self.datetime_date_to_string(departure_date)}T00:00:00</ns:DepartureDateTime>
                    <ns:OriginLocation LocationCode="{origin}" CodeContext="IATA" />
                    <ns:DestinationLocation LocationCode="{destination}" CodeContext="IATA" />
                    <ns:TravelPreferences SmokingAllowed="false">
                        <ns:CabinPref PreferLevel="Preferred" Cabin="Y"/>
                    </ns:TravelPreferences>
                </ns:OriginDestinationInformation>
                <ns:TravelerInfoSummary>
                    <ns:AirTravelerAvail>
                        <ns:PassengerTypeQuantity Code="ADT" Quantity="{adult_count}"/>
                        <ns:PassengerTypeQuantity Code="CHD" Quantity="{child_count}"/>
                        <ns:PassengerTypeQuantity Code="INF" Quantity="{infant_count}"/>
                    </ns:AirTravelerAvail>
                </ns:TravelerInfoSummary>
            </ns:OTA_AirAvailRQ>
        """

        # MAKING GET REQUEST FOR AVAIL FLIGHTS

        data = self.config.post(data=request_data)

        root = ElementTree.fromstring(data['data'])

        OTA_AirAvailRS = root[0][0]

        
        errors = OTA_AirAvailRS.find(f'{self.BASE_SCHEMA_URL}Errors')

        for error in errors:
            print(error.text, error.attrib)

        
        quotedItinerary = OTA_AirAvailRS.find(f".//{self.BASE_SCHEMA_URL}PricedItineraries")
        if (quotedItinerary==None):
            return self._flights

        source_info = AccelAeroSourceInfo(
            adult_count=adult_count,
            child_count=child_count,
            infant_count=infant_count,
            departure_date=departure_date,
            origin=origin,
            destination=destination,
            cabin_of_service='Y'
        )

        quotedItineraryOriginDestinationOptions = quotedItinerary.find(f".//{self.BASE_SCHEMA_URL}OriginDestinationOptions")
        originDestinationInformations = OTA_AirAvailRS.findall(f"{self.BASE_SCHEMA_URL}OriginDestinationInformation")

        getPriceClass = GetPrice(self.client)
        transaction_identifier = OTA_AirAvailRS.attrib.get('TransactionIdentifier')
        for originDestinationInformation in originDestinationInformations:

            originDestinationOptions = originDestinationInformation.find(f".//{self.BASE_SCHEMA_URL}OriginDestinationOptions")
            if originDestinationOptions == quotedItineraryOriginDestinationOptions:
                self._flights.append(getPriceClass.create_offer(quotedItinerary,source_info))
            else: 
                created_offer = getPriceClass.xml_quote(originDestinationOptions,transaction_identifier,adult_count, child_count, infant_count,'ONE_WAY',source_info)
                if created_offer:
                    self._flights.append(created_offer)
            

        return self._flights
