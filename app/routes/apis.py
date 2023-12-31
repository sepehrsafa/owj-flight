import uuid
from typing import Annotated

from app.models import APIs as APIModel
from app.schemas import APIRequest, FlightAPIResponse, FlightAPIsResponse
from fastapi import APIRouter, HTTPException, Path, Security, Depends

from owjcommon.dependencies import get_trace_id, pagination
from owjcommon.exceptions import OWJException, OWJPermissionException
from owjcommon.response import responses
from owjcommon.logger import TraceLogger
from owjcommon.models import get_paginated_results
from owjcommon.schemas import Response

logger = TraceLogger(__name__)

router = APIRouter(
    tags=["Flight APIs"],
)


# create create, update, delete, get, list
@router.post("", response_model=FlightAPIResponse, responses=responses)
async def create_flight_api(request: APIRequest, trace_id=Depends(get_trace_id)):
    """
    This Method is for creating a flight api.
    """
    logger.debug(f"Creating flight api with request {request.dict()}", trace_id)
    api = await APIModel.create(**request.dict())
    return FlightAPIResponse(data=api)


@router.get("", response_model=FlightAPIsResponse, responses=responses)
async def list_flight_apis(
    trace_id=Depends(get_trace_id), pagination=Depends(pagination)
):
    logger.debug("Listing flight apis", trace_id)

    apis = await get_paginated_results(
        APIModel, pagination["offset"], pagination["size"]
    )
    return apis


@router.get("/{uuid}", response_model=FlightAPIResponse, responses=responses)
async def get_flight_api(
    uuid: uuid.UUID = Path(
        ..., description="API UUID", example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    ),
    trace_id=Depends(get_trace_id),
):
    logger.debug(f"Getting flight api with uuid {uuid}", trace_id)
    api = await APIModel.get(uuid=uuid)
    return FlightAPIResponse(data=api)


@router.put("/{uuid}", response_model=FlightAPIResponse, responses=responses)
async def update_flight_api(
    request: APIRequest,
    uuid: uuid.UUID = Path(
        ..., description="API ID", example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    ),
    trace_id=Depends(get_trace_id),
):
    logger.debug(f"Updating flight api with request {request.dict()}", trace_id)
    api = await APIModel.get(uuid=uuid)
    api = await api.update_from_dict(request.dict()).save()
    return FlightAPIResponse(data=api)


@router.delete("/{uuid}", response_model=Response, responses=responses)
async def delete_flight_api(
    uuid: uuid.UUID = Path(
        ..., description="API ID", example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    ),
    trace_id=Depends(get_trace_id),
):
    logger.debug(f"Deleting flight api with uuid {uuid}", trace_id)
    api = await APIModel.get(uuid=uuid)
    await api.delete()
    return Response()
