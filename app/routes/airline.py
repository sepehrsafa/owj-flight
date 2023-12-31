import uuid
from typing import Annotated

from app.models import Airline as AirlineModel
from app.schemas import (
    AirlineRequest,
    AirlineResponse,
    AirlinesResponse,
    AirlineFilters,
)
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security

from owjcommon.dependencies import get_trace_id, pagination
from owjcommon.logger import TraceLogger
from owjcommon.models import get_paginated_results_with_filter
from owjcommon.response import responses
from owjcommon.schemas import Response
from owjcommon.enums import UserPermission, UserSet, UserTypeChoices
from app.services.auth import check_user_set, get_current_user


logger = TraceLogger(__name__)

router = APIRouter(
    tags=["Airline"],
)


# create airline
@router.post("", response_model=AirlineResponse, responses=responses)
async def create_airline(
    request: AirlineRequest,
    trace_id=Depends(get_trace_id),
    current_user=Security(get_current_user, scopes=[UserPermission.AIRLINE_CREATE]),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: AIRLINE:CREATE
    """
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug(f"Creating airline with request {request.dict()}", trace_id)
    airline = await AirlineModel.create(**request.dict(exclude_unset=True))
    return AirlineResponse(data=airline)


# list airlines
@router.get("", response_model=AirlinesResponse, responses=responses)
async def list_airlines(
    trace_id=Depends(get_trace_id),
    pagination=Depends(pagination),
    filters=Depends(AirlineFilters),
    user_account=Security(get_current_user, scopes=[UserPermission.AIRLINE_READ]),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: AIRLINE:READ
    """
    check_user_set(user_account, UserSet.AGENCY)
    logger.debug("Listing airlines", trace_id)
    airlines = await get_paginated_results_with_filter(
        AirlineModel,
        pagination["offset"],
        pagination["size"],
        user_filters=filters.dict(exclude_unset=True),
    )
    return airlines


# get airline
@router.get("/{id}", response_model=AirlineResponse, responses=responses)
async def get_airline(
    id: int = Path(..., description="Airline ID", example=1),
    trace_id=Depends(get_trace_id),
    user_account=Security(get_current_user, scopes=[UserPermission.AIRLINE_READ]),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: AIRLINE:READ
    """
    check_user_set(user_account, UserSet.AGENCY)
    logger.debug(f"Getting airline with id {id}", trace_id)
    airline = await AirlineModel.get_or_exception(id=id)
    return AirlineResponse(data=airline)


# update airline
@router.put("/{id}", response_model=AirlineResponse, responses=responses)
async def update_airline(
    request: AirlineRequest,
    id: int = Path(..., description="Airline ID", example=1),
    trace_id=Depends(get_trace_id),
    user_account=Security(get_current_user, scopes=[UserPermission.AIRLINE_UPDATE]),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: AIRLINE:UPDATE
    """
    check_user_set(user_account, UserSet.AGENCY)
    logger.debug(f"Updating airline with id {id}", trace_id)
    airline = await AirlineModel.get_or_exception(id=id)
    await airline.update_from_dict(request.dict(exclude_unset=True)).save()
    return AirlineResponse(data=airline)


# delete airline
@router.delete("/{id}", response_model=Response, responses=responses)
async def delete_airline(
    id: int,
    trace_id=Depends(get_trace_id),
    user_account=Security(get_current_user, scopes=[UserPermission.AIRLINE_DELETE]),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: AIRLINE:DELETE
    """
    check_user_set(user_account, UserSet.AGENCY)
    logger.debug(f"Deleting airline with id {id}", trace_id)
    airline = await AirlineModel.get_or_exception(id=id)
    await airline.delete()
    return Response()
