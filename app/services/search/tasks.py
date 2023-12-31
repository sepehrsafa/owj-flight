from app.celery import app
from app.schemas import FlightSearchRequest, FlightSearchResponse
from app.models import APIs
from app.enums import APIClient
from app.apis import Charter724Client, AccelAeroClient
import uuid
from owjcommon.logger import TraceLogger
import json
from app.services.utils import get_api_client

logger = TraceLogger(__name__)

api_clients = {
    APIClient.CHARTER724: Charter724Client,
    APIClient.ACCELAERO: AccelAeroClient,
}

clients_instances = {}


@app.task(queue="search_queue")
def simple_add(x, y):
    return x + y


@app.task(queue="search_queue")
def api_search(request, api, trace_id):
    # logger.info(f"Starting search with celery id {self.request.id}, request {request}, and api {api}", trace_id)
    request = json.loads(request)
    api = json.loads(api)
    request = FlightSearchRequest(**request)
    api = APIs(**api)

    client = get_api_client(api, trace_id)
    offers = client.search(request)
    logger.info("Finished search with request.", trace_id)

    # for all items in res call .json() and save in a list
    json_offers = []
    for offer in offers:
        json_offers.append(offer.json())

    return json_offers
