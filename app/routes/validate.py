import uuid
from typing import Annotated

from app.schemas import FlightValidateRequest, FlightValidateResponse
from app.services.validate import validate_fares
from fastapi import APIRouter, HTTPException, Path, Security

from owjcommon.enums import UserPermission
from owjcommon.exceptions import OWJException, OWJPermissionException
from owjcommon.response import responses

router = APIRouter(
    tags=["Flight Validate"],
)


# create create, update, delete, get, list
@router.post("", response_model=FlightValidateResponse, responses=responses)
async def validate_flight(request: FlightValidateRequest):
    return await validate_fares(request, "trace_id")
