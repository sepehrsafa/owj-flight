import uuid
from typing import Annotated

from app.models import Airport as AirportModel
from app.schemas import AirportRequest, AirportResponse, AirportsResponse
from fastapi import APIRouter, Depends, HTTPException, Path, Security

# import Q from tortoise
from tortoise.expressions import Q

from owjcommon.dependencies import pagination, get_trace_id
from owjcommon.models import get_paginated_results
from owjcommon.response import responses
from owjcommon.schemas import Response
from owjcommon.logger import TraceLogger

logger = TraceLogger(__name__)
router = APIRouter(
    tags=["AutoFill"],
)


# create a search endpoint that takes in a string and returns a list of airports
@router.get("/{search}", response_model=AirportsResponse, responses=responses)
async def search_airport(
    search: str = Path(..., description="Airport Search", example="LAX"),
    trace_id=Depends(get_trace_id),
):
    """
    This Method is for searching an airport.
    """
    logger.debug(f"Searching airport with search {search}", trace_id)
    # search if name_fa, name_en, iata_code, or icao_code contains search, or if city.name_fa or city.name_en contains search
    airports = await AirportModel.filter(
        Q(name_fa__icontains=search)
        | Q(name_en__icontains=search)
        | Q(iata_code__icontains=search)
        | Q(icao_code__icontains=search)
        | Q(city__name_fa__icontains=search)
        | Q(city__name_en__icontains=search)
    ).prefetch_related("city")
    return AirportsResponse(items=airports, total_pages=len(airports))
