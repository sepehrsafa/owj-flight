import uuid
from typing import Annotated

from app.schemas import FlightBookRequest, BookingResponse
from fastapi import APIRouter, HTTPException, Path, Security

from owjcommon.enums import UserPermission
from owjcommon.exceptions import OWJException, OWJPermissionException
from owjcommon.response import responses

router = APIRouter(
    tags=["Flight Book"],
)


# create create, update, delete, get, list
@router.post("", response_model=BookingResponse, responses=responses)
async def book(request: FlightBookRequest):
    return
