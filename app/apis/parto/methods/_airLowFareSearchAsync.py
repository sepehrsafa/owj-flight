
import concurrent
import datetime
import logging
from ..exceptions import PartoInvalidSessionException
from apps.flights.choices import *
from apps.finance.choices import CurrencyTypeChoices
from apps.flights.services.search.flight_offer import *
from decimal import Decimal
from .maps import FareTypeChoicesMap, PaxTypeChoicesMap, CabinClassChoicesMap
logger = logging.getLogger(__name__)


class AirLowFareSearchAsync:
  method_name = 'Rest/Air/AirLowFareSearchAsync'

  def __init__(self, client):
      self.client = client
      self.config = client.config
      self._offer_dict = {}

  @staticmethod
  def datetime_to_string(data):
      '''
      Convert date and time from string to datetime object
      '''
      return data.strftime('%Y-%m-%dT00:00:00')

  @staticmethod
  def string_to_datetime(data):
      '''
      Convert date and time from string to datetime object
      '''
      return datetime.datetime.strptime(data, '%Y-%m-%dT%H:%M:%S')

  def create_key(self, data):
    key = ""
    is_charter = False
    for origin_destination in data:
      for flight_segment in origin_destination.get('FlightSegments'):
        marketing_airline_code = flight_segment.get('MarketingAirlineCode')
        flight_number = flight_segment.get('FlightNumber').replace(marketing_airline_code, '')
        departure_date = flight_segment.get('DepartureDateTime')
        operating_airline_code = flight_segment.get('OperatingAirline').get('Code')
        operating_airline_flight_number = flight_segment.get('OperatingAirline').get('FlightNumber')
        operating_airline_flight_number.replace(operating_airline_code, '') if operating_airline_flight_number else flight_number
        is_charter = flight_segment.get('IsCharter')
        key += f'{marketing_airline_code}${flight_number}${departure_date}${operating_airline_code}${operating_airline_flight_number}$'
    return key, is_charter

  def create_offer(self, data: 'OriginDestinationOptions'):
    offer = Offer()
    for origin_destination_id, origin_destination in enumerate(data):
      itinerary = Itinerary(origin_destination_id+1)
      for flight_segment_id, flight_segment in enumerate(origin_destination.get('FlightSegments')):
        stops = []
        for stop in flight_segment.get('TechnicalStops'):
            stops.append(
                Stop(
                    iata_code=stop.get('ArrivalAirport'),
                    arrival_at=stop.get('ArrivalDateTime'),
                    departure_at=stop.get('DepartureAirport'),
                )
            )
        departure = Location(
          iata_code=flight_segment.get('DepartureAirportLocationCode'),
          at=self.string_to_datetime(flight_segment.get('DepartureDateTime')),
        )
        arrival = Location(
          iata_code=flight_segment.get('ArrivalAirportLocationCode'),
          at=self.string_to_datetime(flight_segment.get('ArrivalDateTime')),
        )
        marketing_airline_code = flight_segment.get('MarketingAirlineCode')
        flight_number = flight_segment.get('FlightNumber').replace(marketing_airline_code, '')
        operating_airline_code = flight_segment.get('OperatingAirline').get('Code')
        operating_airline_flight_number = flight_segment.get('OperatingAirline').get('FlightNumber')
        operating_airline_flight_number = operating_airline_flight_number.replace(operating_airline_code, '') if operating_airline_flight_number else flight_number
        segment = Segment(
          segment_id=origin_destination_id+flight_segment_id+1,
          departure=departure,
          arrival=arrival,
          operating_airline=operating_airline_code,
          operating_flight_number=operating_airline_flight_number,
          marketing_airline=marketing_airline_code,
          flight_number=flight_number,
          equipment=flight_segment.get('OperatingAirline').get('Equipment'),
          stops=stops,
          stop_quantity=flight_segment.get('StopQuantity'),
        )
        itinerary.add_segment(segment)
      offer.add_itinerary(itinerary)
    return offer

  def get_offer(self, data: 'OriginDestinationOptions'):
    key, is_charter = self.create_key(data)

    if key in self._offer_dict:
      key_data = self._offer_dict.get(key)
      if(key_data.get('is_charter') == True and is_charter == False):
        key_data['is_charter'] = False
        new_offer = self.create_offer(data)
        offer = key_data.get('offer')
        offer.itineraries = new_offer.itineraries
        return offer
      
      return key_data.get('offer')

    offer = self.create_offer(data)
    self._offer_dict[key] = {'is_charter': is_charter, 'offer': offer}
    return offer

  def create_fare(self, data: 'PricedItineraries'):
    air_itinerary_pricing = data.get('AirItineraryPricingInfo')
    origin_destinations = data.get('OriginDestinationOptions')

    is_charter = False
    segment_info = []

    for origin_destination_id, origin_destination in enumerate(origin_destinations):
      for flight_segment_id, flight_segment in enumerate(origin_destination.get('FlightSegments')):
        segment_info.append(
            SegmentInfo(
                segment_id=origin_destination_id+flight_segment_id+1,
                segment_key=flight_segment.get('DepartureAirportLocationCode')+"/"+flight_segment.get('ArrivalAirportLocationCode'),
                cabin=CabinClassChoicesMap.get(flight_segment.get('CabinClassCode')),
                booking_class=flight_segment.get('ResBookDesigCode'),
                fare_basis=flight_segment.get('ResBookDesigCode'),
            )
        )
        is_charter = flight_segment.get('IsCharter')

    fare = Fare(
      fare_type=FareTypeChoicesMap.get(20) if is_charter else FareTypeChoicesMap.get(air_itinerary_pricing.get('FareType')),
      validating_airline=data.get('ValidatingAirlineCode'),
      is_refundable=False if data.get('IsRefundable') == 2 else True,
      instant_ticketing_required=True if air_itinerary_pricing.get('FareType') == 4 else False,
      source=Source(system_id=self.config._system_code,api_details=data.get('FareSourceCode'))
    )

    for ptc_breakdown in air_itinerary_pricing.get('PtcFareBreakdown'):
    
      service_fee = Decimal(ptc_breakdown.get('PassengerFare').get('ServiceTax'))
      system_fare = SystemFare(
          base=Decimal(ptc_breakdown.get('PassengerFare').get('BaseFare')),
          total=Decimal(ptc_breakdown.get('PassengerFare').get('TotalFare')),
          system_commission=Decimal(ptc_breakdown.get('PassengerFare').get('Commission')),
          taxes=[Tax(Decimal(tax.get('Amount'))) for tax in ptc_breakdown.get('PassengerFare').get('Taxes')],
          services=[Service(service_fee)] if service_fee!=0.0 else None,
          currency=CurrencyTypeChoices[ptc_breakdown.get('PassengerFare').get('Currency')],
      )
      fare.add_pax_info(
        PaxInfo(
          pax_type=PaxTypeChoicesMap.get(ptc_breakdown.get('PassengerTypeQuantity').get('PassengerType')),
          number_of_pax=ptc_breakdown.get('PassengerTypeQuantity').get('Quantity'),
          system_fare=system_fare,
          details_per_segment=segment_info
        )
      )
    return fare

  def search_oneway(self, origin, destination, adult_count, child_count, infant_count, departure_date):
    data = {
        "PricingSourceType": 0,
        "RequestOption": 2,
        "AdultCount": adult_count,
        "ChildCount": child_count,
        "InfantCount": infant_count,
        "TravelPreference": {
            "CabinType": 1,
            "MaxStopsQuantity": 0,
            "AirTripType": 1,
        },
        "OriginDestinationInformations": [
            {
                "DepartureDateTime": self.datetime_to_string(departure_date),
                "DestinationLocationCode": destination,
                "DestinationType": 0,
                "OriginLocationCode": origin,
                "OriginType": 0
            }
        ]
    }

    data = self.config.post(self.method_name, data=data)

    for flight in data.get('PricedItineraries', []):

      try:
        offer = self.get_offer(flight.get('OriginDestinationOptions'))
        offer.add_fare(self.create_fare(flight))

      except Exception as e:
        print(e)
        print(flight)
        print(offer)

    
    return_data = []
    
    for key, value in self._offer_dict.items():
        return_data.append(value.get('offer')) 
    

    return return_data