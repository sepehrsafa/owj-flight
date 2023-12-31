from apps.flights.models import FlightSale, SharedFlightApi
from apps.flights.services.client import FlightAPIsClient
from logging import getLogger
logger = getLogger(__name__)
def update_booking(flight_sale_id,shared_api_id):

    flight_sale = FlightSale.objects.get(id=flight_sale_id)
    shared_api = SharedFlightApi.objects.get(id=shared_api_id).api
    client = FlightAPIsClient.get_client(shared_api)
    logger.debug(msg='Calling update booking for flight sale: %s' % flight_sale_id)
    client._update_booking(flight_sale)
