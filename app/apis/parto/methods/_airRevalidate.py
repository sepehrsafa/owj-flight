
import datetime
import logging
from apps.flights.choices import *
from apps.finance.choices import CurrencyTypeChoices
from apps.flights.services.search.flight_offer import *
from decimal import Decimal
from .maps import FareTypeChoicesMap, PaxTypeChoicesMap, CabinClassChoicesMap
logger = logging.getLogger(__name__)


class AirRevalidate:
  method_name = 'Rest/Air/AirRevalidate'

  def __init__(self, client):
      self.client = client
      self.config = client.config


  @staticmethod
  def string_to_datetime(data):
      '''
      Convert date and time from string to datetime object
      '''
      return datetime.datetime.strptime(data, '%Y-%m-%dT%H:%M:%S')


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

  def revalidate(self, fare_source_code):
    
    data = {
        "FareSourceCode": fare_source_code,
    }

    data = self.config.post(self.method_name, data=data)
    '''{'Success': False, 'Error': {'Id': 'Err0104006', 'Message': 'This result is not valid anymore,Please search again.', 'BaseCategory': None, 'Category': None}, 'ClientBalance': 0.0, 'Services': [], 'PricedItinerary': None, 'AdditionalData': None}'''
    

    priced_itinerary = data.get('PricedItinerary')
    origin_destinations = priced_itinerary.get('OriginDestinationOptions')
    offer = self.create_offer(origin_destinations)
    offer.add_fare(self.create_fare(priced_itinerary))
    return offer