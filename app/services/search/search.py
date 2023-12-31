from app.schemas import FlightSearchRequest, FlightSearchResponse
from app.models import APIs
from app.enums import APIClient
from app.apis import Charter724Client, AccelAeroClient
import uuid
from .tasks import api_search, simple_add
from app.schemas import API, SearchCache, SearchCacheItem
from owjcommon.logger import TraceLogger
import json
from datetime import datetime, timedelta
import time
from app.services.utils import get_api_client

CELERY_TASK_EXPIRE_IN_MINUTES = 10
CACHE_KEY_EXPIRE_IN_MINUTES = 5
SEARCH_ID_EXPIRE_IN_MINUTES = 20

logger = TraceLogger(__name__)


async def search(request: FlightSearchRequest, trace_id) -> FlightSearchResponse:
    from app.main import redis

    logger.debug(f"Starting search with request {request.dict()}", trace_id)
    simple_add.delay(1, 2)
    active_apis = await APIs.filter(is_active=True)
    logger.debug(f"Found {len(active_apis)} active apis", trace_id)
    search_id = uuid.uuid4()
    logger.debug(f"Search id is {search_id}", trace_id)

    available_offers = []
    new_cache_items = []
    available_cache_items = []
    available_cache_items_not_ready = []
    available_cache_items_ready = []

    for api in active_apis:
        # check if client is in clients_instances
        client = get_api_client(api, trace_id)
        cache_key = client.get_search_cache_key(request)
        # check if cache_key is in cache
        cache_response = await redis.get(cache_key)
        if cache_response:
            logger.debug(f"Cache key {cache_key} for api {api.id} is valid", trace_id)
            cache_response = json.loads(cache_response)
            cache_item = SearchCacheItem(**cache_response)
            available_cache_items.append(cache_item)
            continue

        logger.debug(
            f"Cache key {cache_key} for api {api.id} is not in cache", trace_id
        )
        # create task for api_search
        _api = await API.from_tortoise_orm(api)
        result = api_search.delay(request.json(), _api.json(), trace_id)
        # save task_id in cache
        utc_now = datetime.utcnow()
        latest_know_celery_task_id_expiry_utc = utc_now + timedelta(
            minutes=CELERY_TASK_EXPIRE_IN_MINUTES
        )
        cache_item = SearchCacheItem(
            search_key=cache_key,
            been_fetched=False,
            latest_known_celery_task_id=result.task_id,
            latest_know_celery_task_id_expiry_utc=latest_know_celery_task_id_expiry_utc,
            api_id=api.id,
        )
        await redis.set(
            cache_key, cache_item.json(), ex=CACHE_KEY_EXPIRE_IN_MINUTES * 60
        )
        new_cache_items.append(cache_item)
        logger.debug(
            f"Task created for api {api.id} with celery id {result.task_id}", trace_id
        )

    for available_cache_item in available_cache_items:
        # get result from celery
        logger.debug(
            f"Getting result from celery for available cache item {available_cache_item.json()}",
            trace_id,
        )
        # check if task is finished
        is_ready = api_search.AsyncResult(
            available_cache_item.latest_known_celery_task_id
        ).ready()
        if not is_ready:
            logger.debug(
                f"Task {available_cache_item.latest_known_celery_task_id} is not ready yet",
                trace_id,
            )
            available_cache_items_not_ready.append(available_cache_item)
            continue
        logger.debug(
            f"Task {available_cache_item.latest_known_celery_task_id} is ready",
            trace_id,
        )
        # get result from celery
        task_data = api_search.AsyncResult(
            available_cache_item.latest_known_celery_task_id
        ).get()
        available_cache_items_ready.append(available_cache_item)
        available_offers += [json.loads(item) for item in task_data]

    # set fetched=True for available_cache_items_ready using list comprehension
    [setattr(item, "been_fetched", True) for item in available_cache_items_ready]
    total_unfinished_items = len(available_cache_items_not_ready) + len(new_cache_items)
    total_items = (
        new_cache_items + available_cache_items_ready + available_cache_items_not_ready
    )
    search_cache = SearchCache(
        items=total_items,
        search_track_id=trace_id,
        has_all_tasks_finished=total_unfinished_items == 0,
    )

    await redis.set(
        f"flight_search:{search_id}",
        search_cache.json(),
        ex=SEARCH_ID_EXPIRE_IN_MINUTES * 60,
    )

    return FlightSearchResponse(search_id=search_id, offers=available_offers)


async def get_results(search_id, fetch_all, trace_id):
    from app.main import redis

    available_offers = []
    t1 = time.time()
    cache_response = await redis.get(f"flight_search:{search_id}")
    t2 = time.time()
    logger.debug(f"Redis get took {t2 - t1} seconds", trace_id)
    logger.debug(
        f"Cache response for search id {search_id} is {cache_response}", trace_id
    )
    if cache_response:
        cache_response = json.loads(cache_response)
        search_cache = SearchCache(**cache_response)
        if (search_cache.has_all_tasks_finished and fetch_all) or not fetch_all:
            for cache_item in search_cache.items:
                t3 = time.time()
                if fetch_all or not cache_item.been_fetched:
                    if not cache_item.been_fetched:
                        check_task = api_search.AsyncResult(
                            cache_item.latest_known_celery_task_id
                        ).ready()

                        if not check_task:
                            continue

                    task_data = api_search.AsyncResult(
                        cache_item.latest_known_celery_task_id
                    ).get()
                    t4 = time.time()
                    logger.debug(
                        f"Getting result from celery for cache item {cache_item.json()} took {t4 - t3} seconds",
                        trace_id,
                    )

                    cache_item.been_fetched = True
                    available_offers += [json.loads(item) for item in task_data]

        # check if all tasks are finished
        search_cache.has_all_tasks_finished = all(
            [item.been_fetched for item in search_cache.items]
        )
        t5 = time.time()
        await redis.set(
            f"flight_search:{search_id}",
            search_cache.json(),
            ex=SEARCH_ID_EXPIRE_IN_MINUTES * 60,
        )
        t6 = time.time()
        logger.debug(f"Redis set took {t6 - t5} seconds", trace_id)

        return FlightSearchResponse(
            search_id=search_id,
            offers=available_offers,
            is_finished=search_cache.has_all_tasks_finished,
        )

    return FlightSearchResponse(
        search_id=search_id,
        offers=[],
        is_finished=False,
    )
