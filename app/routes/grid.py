from fastapi import APIRouter, HTTPException, Security, Path
from typing import Annotated
from owjcommon.enums import UserPermission
from owjcommon.response import responses
from owjcommon.exceptions import OWJException, OWJPermissionException
from app.schemas import (
    FlightGridRequest,
    FlightGridResponse,
    FlightSearchRequest,
    FlightSearchDataResponse,
)
import uuid
from app.apis import Charter724Client

from app.apis import AccelAeroClient

router = APIRouter(
    tags=["Flight Grid"],
)


testClient = Charter724Client(
    id="test",
    url="https://api.charter725.ir",
    key="demo",
    secret="demo",
    extra={},
    search_timeout=60,
)
mahanClient = AccelAeroClient(
    id="s",
    url="https://reservations.mahan.aero/webservices/services/AAResWebServices",
    key="PARSEOWJ13",
    secret="Sepehr8102$",
    extra={
        "terminal_id": "PARSEOWJ",
        "requestor_id_type": "2",
        "booking_chanel": "14",
    },
    search_timeout=60,
)


@router.post("", response_model=FlightGridResponse, responses=responses)
async def grid_search(request: FlightGridRequest):
    """
    This Method is for grid search.
    It provides the cheapest price for each day between the given dates.
    """
    res = testClient.grid_search(request)

    return FlightGridResponse(data=res)
