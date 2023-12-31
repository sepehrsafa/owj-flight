from fastapi import APIRouter, HTTPException, Security, Path, Depends
from typing import Annotated
from owjcommon.enums import UserPermission
from owjcommon.response import responses
from owjcommon.exceptions import OWJException, OWJPermissionException
from app.schemas import (
    FlightSearchRequest,
    FlightSearchResponse,
    FlightSearchDataResponse,
)
import uuid
from app.services.search import search, get_results
from owjcommon.dependencies import get_trace_id
from app.apis import Charter724Client, AccelAeroClient

router = APIRouter(
    tags=["Flight Search"],
)


# create create, update, delete, get, list
@router.post("", response_model=FlightSearchResponse, responses=responses)
async def create_flight_search(
    request: FlightSearchRequest, trace_id=Depends(get_trace_id)
):
    """
    This Method is for flight search.
    It provides search id for the search request which can be used to get the results.
    It also provides any flights that are available at the time of the request
    """
    return await search(request, trace_id)


# create create, update, delete, get, list
@router.post("test", response_model=FlightSearchResponse, responses=responses)
async def create_flight_search_2(
    request: FlightSearchRequest, trace_id=Depends(get_trace_id)
):
    """
    This Method is for flight search.
    It provides search id for the search request which can be used to get the results.
    It also provides any flights that are available at the time of the request
    """
    data = AccelAeroClient(
        id="1",
        url="https://reservations.mahan.aero/webservices/services/AAResWebServices",
        key="PARSEOWJ13",
        secret="Sepehr8102$",
        extra={
            "terminal_id": "PARSEOWJ",
            "requestor_id_type": "2",
            "booking_chanel": "14",
        },
        search_timeout=60,
    ).search(request)
    print(data)
    return FlightSearchResponse(search_id=uuid.uuid4(), offers=data)


@router.get("/{searchId}", response_model=FlightSearchDataResponse, responses=responses)
async def get_flight_search(
    searchId: uuid.UUID = Path(
        ..., description="Search ID", example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    ),
    fetch_all: bool = False,
    trace_id=Depends(get_trace_id),
):
    """
    This Method is for getting the results of a search.
    It provides the results of the search with the given search id.
    """

    return await get_results(searchId, fetch_all, trace_id)
