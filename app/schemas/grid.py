from decimal import Decimal
from typing import Optional, Union

from app.config import settings
from app.enums import CabinType, FareType, IATACodeType, OfferType
from pydantic import UUID4, BaseModel, Field, conint, model_validator, validator

from owjcommon.enums import CurrencyChoices
from owjcommon.schemas import Response


class FlightGridRequest(BaseModel):
    origin: str = Field(
        ...,
        description="Origin IATA code",
        example="THR",
    )
    origin_type: IATACodeType = Field(
        IATACodeType.AIRPORT,
        description="Origin IATA code type",
        validation_alias="originType",
    )
    destination: str = Field(
        ...,
        description="Destination IATA code",
        example="KER",
    )
    destination_type: IATACodeType = Field(
        IATACodeType.AIRPORT,
        description="Destination IATA code type",
        validation_alias="destinationType",
    )
    type: OfferType = Field(
        OfferType.ONE_WAY,
        description="Type of offer",
        example=OfferType.ONE_WAY,
    )
    cabin_type: CabinType = Field(
        CabinType.ECONOMY,
        description="Cabin type",
        validation_alias="cabinType",
    )
    currency: CurrencyChoices = Field(
        CurrencyChoices.IRR,
        description="Currency to be used for pricing",
    )
    from_date: str = Field(
        ...,
        description="From date in YYYY-MM-DD format",
        serialization_alias="fromDate",
        example="2023-12-30",
        validation_alias="fromDate",
    )
    to_date: Union[str, None] = Field(
        None,
        description="To date in YYYY-MM-DD format",
        serialization_alias="toDate",
        example="2023-12-30",
        validation_alias="toDate",
    )


class FlightGridData(BaseModel):
    departure_date: str = Field(
        ...,
        description="Date",
        example="2023-12-30",
    )
    return_date: Union[str, None] = Field(
        None,
        description="Return date in YYYY-MM-DD format",
        serialization_alias="returnDate",
        example="2023-12-31",
    )
    type: OfferType = Field(
        OfferType.ONE_WAY,
        description="Type of offer",
        example=OfferType.ONE_WAY,
    )
    price: Decimal = Field(
        ...,
        description="Price",
        example="1000.00",
    )
    commission: Union[Decimal, None] = Field(
        None,
        description="Commission",
        example="100.00",
    )
    type: Union[FareType, None] = Field(
        None,
        description="Fare type",
        example=FareType.PUBLIC,
    )
    currency: str = Field(
        ...,
        description="Currency",
        example="IRR",
    )
    airline: Union[str, None] = Field(
        None,
        description="Airline",
        example="IR",
    )


class FlightGridResponse(Response):
    data: list[FlightGridData] = Field(
        ...,
        description="List of flight grid data",
    )
