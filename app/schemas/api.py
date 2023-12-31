from decimal import Decimal
from typing import Optional

from app.config import settings
from app.enums import APIClient
from pydantic import UUID4, BaseModel, Field, conint, model_validator, validator

from owjcommon.enums import CurrencyChoices
from owjcommon.schemas import Response

from tortoise.contrib.pydantic import pydantic_model_creator
from app.models import APIs as APIsModel

APIRequest = pydantic_model_creator(
    APIsModel, name="APIRequest", exclude=("id", "uuid")
)


API = pydantic_model_creator(APIsModel, name="API")


class FlightAPIsResponse(Response):
    items: list[API]


class FlightAPIResponse(Response):
    data: API
