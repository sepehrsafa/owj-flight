from app.models import APIs
from app.enums import APIClient
from app.apis import Charter724Client, AccelAeroClient
import uuid
from app.schemas import (
    FlightValidateRequest,
    SearchCache,
    SearchCacheItem,
    FlightValidateResponse,
)
from owjcommon.logger import TraceLogger
import json
from datetime import datetime, timedelta
import time
from app.services.utils import get_api_client
from app.services.search.tasks import api_search
from app.schemas import Offer, Fare

logger = TraceLogger(__name__)


async def validate_fares(
    request: FlightValidateRequest, trace_id
) -> FlightValidateResponse:
    from app.main import redis

    logger.debug(f"Starting validate with request {request.dict()}", trace_id)
    cache_data = await redis.get(f"flight_search:{request.search_id}")
    cache_data = json.loads(cache_data)
    cache_data = SearchCache(**cache_data)
    requested_offers = []
    for key in request.keys:
        key_array = key.split(",")
        api_id = key_array[0]
        # loop to find all cache items with this api id, then loop through them to find the one with the same key
        found_items = []
        for cache_item in cache_data.items:
            if str(cache_item.api_id) == str(api_id):
                # get cache data from celery
                task_data = api_search.AsyncResult(
                    cache_item.latest_known_celery_task_id
                ).get()
                offers = [json.loads(item) for item in task_data]
                for offer in offers:
                    for fare in offer.get("fares", []):
                        if fare.get("key") == key:
                            found_items.append((offer, fare))

        for offer, fare in found_items:
            offer = Offer(**offer)
            fare = Fare(**fare)
            offer.fare = fare
            del offer.fares
            requested_offers.append(offer)

    logger.debug(f"Found {len(requested_offers)} requested offers", trace_id)
    return FlightValidateResponse(offers=requested_offers, search_id=request.search_id)
