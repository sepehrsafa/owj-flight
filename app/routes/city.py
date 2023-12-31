import uuid
from typing import Annotated

from app.models import City as CityModel
from app.schemas import CitiesResponse, CityRequest, CityResponse, CityFilters
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security

from owjcommon.dependencies import pagination, get_trace_id
from owjcommon.models import get_paginated_results_with_filter
from owjcommon.response import responses
from owjcommon.schemas import Response
from owjcommon.logger import TraceLogger
from app.services.auth import check_user_set, get_current_user
from owjcommon.enums import UserPermission, UserSet, UserTypeChoices


logger = TraceLogger(__name__)
router = APIRouter(
    tags=["City"],
)


# create create, update, delete, get, list
@router.post("", response_model=CityResponse, responses=responses)
async def create_city(
    request: CityRequest,
    trace_id=Depends(get_trace_id),
    current_user=Security(get_current_user, scopes=[UserPermission.CITY_CREATE]),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: CITY:CREATE
    """
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug(f"Creating city with request {request.dict()}", trace_id)
    city = await CityModel.create(**request.dict(exclude_unset=True))
    return CityResponse(data=city)


@router.get("", response_model=CitiesResponse, responses=responses)
async def list_cities(
    pagination=Depends(pagination),
    trace_id=Depends(get_trace_id),
    filters=Depends(CityFilters),
    current_user=Security(get_current_user, scopes=[UserPermission.CITY_READ]),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: CITY:READ
    """
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug("Listing cities", trace_id)
    cities = await get_paginated_results_with_filter(
        CityModel,
        pagination["offset"],
        pagination["size"],
        user_filters=filters.dict(exclude_unset=True),
    )
    return cities


@router.get("/{id}", response_model=CityResponse, responses=responses)
async def get_city(
    id: int = Path(..., description="City ID", example=1),
    trace_id=Depends(get_trace_id),
    current_user=Security(get_current_user, scopes=[UserPermission.CITY_READ]),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: CITY:READ
    """
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug(f"Getting city with id {id}", trace_id)
    city = await CityModel.get_or_exception(id=id)
    return CityResponse(data=city)


@router.put("/{id}", response_model=CityResponse, responses=responses)
async def update_city(
    request: CityRequest,
    id: int = Path(..., description="City ID", example=1),
    trace_id=Depends(get_trace_id),
    current_user=Security(get_current_user, scopes=[UserPermission.CITY_UPDATE]),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: CITY:UPDATE
    """
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug(f"Updating city with id {uuid}", trace_id)
    city = await CityModel.get_or_exception(id=id)
    await city.update_from_dict(request.dict(exclude_unset=True)).save()
    return CityResponse(data=city)


@router.delete("/{id}", response_model=Response, responses=responses)
async def delete_city(
    id: int = Path(..., description="City ID", example=1),
    trace_id=Depends(get_trace_id),
    current_user=Security(get_current_user, scopes=[UserPermission.CITY_DELETE]),
):
    """
    Type and Scope:

    - **Type**: AGENCY User Set
    - **Scope**: CITY:DELETE
    """
    check_user_set(current_user, UserSet.AGENCY)
    logger.debug(f"Deleting city with id {id}", trace_id)
    city = await CityModel.get_or_exception(id=id)
    await city.delete()
    return Response()
