import uuid

from app.models import Airport as AirportModel, City as CityModel
from app.schemas import AirportRequest, AirportResponse, AirportsResponse
from fastapi import APIRouter, Depends, HTTPException, Path

from owjcommon.dependencies import pagination, get_trace_id
from owjcommon.models import get_paginated_data_results
from owjcommon.response import responses
from owjcommon.schemas import Response
from owjcommon.logger import TraceLogger

logger = TraceLogger(__name__)
router = APIRouter(
    tags=["Airport"],
)


# create create, update, delete, get, list
@router.post("", response_model=AirportResponse, responses=responses)
async def create_airport(request: AirportRequest, trace_id=Depends(get_trace_id)):
    """
    This Method is for creating an airport.
    """
    logger.debug(f"Creating airport with request {request.dict()}", trace_id)

    # check if city_uuid or city_iata_code is provided
    if request.city_uuid is None and request.city_iata_code is None:
        raise HTTPException(
            status_code=400,
            detail="Either city_uuid or city_iata_code must be provided",
        )

    # check if city_uuid or city_iata_code is valid
    if request.city_uuid is not None:
        city = await CityModel.get(uuid=request.city_uuid)
    else:
        city = await CityModel.get(iata_code=request.city_iata_code)

    airport = await AirportModel.create(**request.dict(), city=city)
    return AirportResponse(data=airport)


@router.get("/{uuid}", response_model=AirportResponse, responses=responses)
async def get_airport(
    uuid: uuid.UUID = Path(
        ..., description="Airport ID", example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    ),
    trace_id=Depends(get_trace_id),
):
    """
    This Method is for getting an airport.
    """
    logger.debug(f"Getting airport with uuid {uuid}", trace_id)
    airport = await AirportModel.get(uuid=uuid)
    return AirportResponse(data=airport)


@router.get("", response_model=AirportsResponse, responses=responses)
async def list_airports(pagination=Depends(pagination), trace_id=Depends(get_trace_id)):
    """
    This Method is for listing airports.
    """
    logger.debug("Listing airports with trace id", trace_id)

    # get all airports with foriegn key city
    data = await AirportModel.get_all_airports()

    print(len(data))

    airports = await get_paginated_data_results(
        data, pagination["offset"], pagination["size"]
    )
    return airports


@router.put("/{uuid}", response_model=AirportResponse, responses=responses)
async def update_airport(
    request: AirportRequest,
    uuid: uuid.UUID = Path(
        ..., description="Airport ID", example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    ),
    trace_id=Depends(get_trace_id),
):
    """
    This Method is for updating an airport.
    """
    logger.debug(f"Updating airport with uuid {uuid}", trace_id)
    airport = await AirportModel.get(uuid=uuid)
    await airport.update_from_dict(request.dict()).save()
    return AirportResponse(data=airport)


@router.delete("/{uuid}", response_model=Response, responses=responses)
async def delete_airport(
    uuid: uuid.UUID = Path(
        ..., description="Airport ID", example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    ),
    trace_id=Depends(get_trace_id),
):
    """
    This Method is for deleting an airport.
    """
    logger.debug(f"Deleting airport with uuid {uuid}", trace_id)
    airport = await AirportModel.get(uuid=uuid)
    await airport.delete()
    return Response()
