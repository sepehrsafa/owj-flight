from app.config import settings
from app.enums import CabinType, IATACodeType
from pydantic import UUID4, BaseModel, Field, conint, model_validator, validator


from owjcommon.enums import CurrencyChoices, CountryChoices
from owjcommon.schemas import Response
from .offer import Offer
from decimal import Decimal
from typing import Optional, Union


class FlightValidateRequest(BaseModel):
    search_id: UUID4 = Field(
        ...,
        description="Search ID",
        example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    )
    keys: list[str] = Field(
        ...,
        description="List of Fare Keys",
        example=["1234567890"],
    )


class Passenger(BaseModel):
    first_name: str = Field(
        "REQUIRED",
        description="First name in English",
        example="John",
    )
    last_name: str = Field(
        "REQUIRED",
        description="Last name in English",
        example="Doe",
    )
    date_of_birth: Optional[str] = Field(
        "OPTIONAL",
        description="Date of birth",
        example="2023-12-30",
    )
    iran_national_id: Optional[str] = Field(
        "REQUIRED",
        description="Iran National ID",
        example="1234567890",
    )
    passport_number: Optional[str] = Field(
        "OPTIONAL",
        description="Passport Number",
        example="1234567890",
    )
    passport_expiry_date: Optional[str] = Field(
        "OPTIONAL",
        description="Passport Expiry Date",
        example="2023-12-30",
    )
    passport_issue_date: Optional[str] = Field(
        "OPTIONAL",
        description="Passport Issue Date",
        example="2023-12-30",
    )
    passport_issuing_country: Optional[str] = Field(
        "OPTIONAL",
        description="Passport Issuing Country",
        example="IR",
    )


class FlightValidateResponse(Response):
    search_id: UUID4 = Field(
        ...,
        description="Search ID",
        example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    )
    offers: list[Offer] = Field(
        ...,
        description="List of offers",
    )

    total_base: Decimal = Field(
        Decimal(0),
        description="Base fare",
        example=1000000,
    )
    total_fees: Decimal = Field(
        Decimal(0),
        description="Total fees",
        example=1000000,
    )
    total_taxes: Decimal = Field(
        Decimal(0),
        description="Total taxes",
        example=1000000,
    )
    total_services: Decimal = Field(
        Decimal(0),
        description="Total service fee",
        example=1000000,
    )
    total_discounts: Decimal = Field(
        Decimal(0),
        description="Total discount",
        example=1000000,
    )
    total: Decimal = Field(
        Decimal(0),
        description="Total fare",
        example=1000000,
    )
    currency: CurrencyChoices = Field(
        CurrencyChoices.IRR,
        description="Currency",
        example=CurrencyChoices.IRR,
    )
    booking_fields: Passenger = Field(
        Passenger(),
        description="Booking Fields",
    )
