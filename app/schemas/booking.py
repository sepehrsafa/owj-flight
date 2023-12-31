from datetime import datetime
from decimal import Decimal
from typing import Optional, Union

from app.config import settings
from app.enums import (
    BookingStatus,
    CabinType,
    DataSource,
    FareType,
    IATACodeType,
    OfferType,
    PassengerStatus,
)
from pydantic import UUID4, BaseModel, Field, conint, root_validator, validator

from owjcommon.enums import CurrencyChoices
from owjcommon.schemas import Password, Response


class BookingPassengerSegment(BaseModel):
    id: int = Field(
        ...,
        description="Passenger Segment ID",
        example=1,
    )
    uuid: UUID4 = Field(
        ...,
        description="Passenger Segment UUID",
        example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    )
    code: str = Field(
        ...,
        description="Code",
        example="IKA/DXB",
    )
    status: PassengerStatus = Field(
        PassengerStatus.UNKNOWN,
        description="Passenger Status",
    )
    pnr: Optional[str] = Field(
        None,
        description="PNR",
        example="ABC123",
    )
    ticket_number: Optional[str] = Field(
        None,
        description="Ticket Number",
        example="ABC123",
    )
    cabin: CabinType = Field(
        CabinType.ECONOMY,
        description="Cabin Type",
    )
    fare_basis: str = Field(
        ...,
        description="Fare Basis",
        example="ABC123",
    )
    booking_class: Optional[str] = Field(
        ...,
        description="Booking Class",
        example="ABC123",
    )
    branded_fare: Optional[str] = Field(
        None,
        description="Branded Fare",
        example="Eco Flex",
    )
    baggage: Optional[str] = Field(
        None,
        description="Baggage",
        example="20KG",
    )
    carryon: Optional[str] = Field(
        None,
        description="Carryon",
        example="7KG",
    )


class BookingPassenger(BaseModel):
    id: int = Field(
        ...,
        description="Passenger ID",
        example=1,
    )
    uuid: UUID4 = Field(
        ...,
        description="Passenger UUID",
        example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    )
    first_name: str = Field(
        ...,
        description="First Name",
        example="John",
    )
    last_name: str = Field(
        ...,
        description="Last Name",
        example="Doe",
    )
    date_of_birth: Optional[datetime] = Field(
        None,
        description="Date of Birth",
    )
    iran_national_id: Optional[str] = Field(
        None,
        description="Iran National ID",
        example="0012345678",
    )
    passport_number: Optional[str] = Field(
        None,
        description="Passport Number",
        example="0012345678",
    )
    passport_expiry_date: Optional[datetime] = Field(
        None,
        description="Passport Expiry Date",
    )
    passport_issue_date: Optional[datetime] = Field(
        None,
        description="Passport Issue Date",
    )
    passport_issuance_country: Optional[IATACodeType] = Field(
        None,
        description="Passport Issuance Country",
    )
    base: Decimal = Field(
        ...,
        description="Base",
        example=1000000,
    )
    tax: Decimal = Field(
        ...,
        description="Tax",
        example=1000000,
    )
    fee: Decimal = Field(
        ...,
        description="Fee",
        example=1000000,
    )
    service: Decimal = Field(
        ...,
        description="Service",
        example=1000000,
    )
    discount: Decimal = Field(
        ...,
        description="Discount",
        example=1000000,
    )
    markup: Decimal = Field(
        ...,
        description="Markup",
        example=1000000,
    )
    commission: Decimal = Field(
        ...,
        description="Commission",
        example=1000000,
    )
    total: Decimal = Field(
        ...,
        description="Total",
        example=1000000,
    )
    currency: CurrencyChoices = Field(
        CurrencyChoices.IRR,
        description="Currency",
    )
    penalty: Decimal = Field(
        ...,
        description="Penalty",
        example=1000000,
    )
    refund_total: Decimal = Field(
        ...,
        description="Refund Total",
        example=1000000,
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp",
    )
    segments: list[BookingPassengerSegment] = Field(
        ...,
        description="Segments",
    )


class BookingStop(BaseModel):
    id: int = Field(
        ...,
        description="Stop ID",
        example=1,
    )
    uuid: UUID4 = Field(
        ...,
        description="Stop UUID",
        example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    )
    airport: str = Field(
        ...,
        description="Airport",
        example="IKA",
    )
    arrival: Optional[datetime] = Field(
        None,
        description="Arrival",
    )
    departure: Optional[datetime] = Field(
        None,
        description="Departure",
    )


class BookingSegment(BaseModel):
    id: int = Field(
        ...,
        description="Segment ID",
        example=1,
    )
    uuid: UUID4 = Field(
        ...,
        description="Segment UUID",
        example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    )
    code: str = Field(
        ...,
        description="Code",
        example="IKA/DXB",
    )
    origin: str = Field(
        ...,
        description="Origin",
        example="IKA",
    )
    destination: str = Field(
        ...,
        description="Destination",
        example="DXB",
    )
    departure: datetime = Field(
        ...,
        description="Departure",
    )
    arrival: datetime = Field(
        ...,
        description="Arrival",
    )
    flight_number: str = Field(
        ...,
        description="Flight Number",
        example="ABC123",
    )
    operating_flight_number: str = Field(
        ...,
        description="Operating Flight Number",
        example="ABC123",
    )
    airline: str = Field(
        ...,
        description="Airline",
        example="ABC123",
    )
    stops: list[BookingStop] = Field(
        ...,
        description="Stops",
    )


class Booking(BaseModel):
    id: int = Field(
        ...,
        description="Booking ID",
        example=1,
    )
    uuid: UUID4 = Field(
        ...,
        description="Booking UUID",
        example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    )
    user: UUID4 = Field(
        ...,
        description="User UUID",
        example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    )
    business: Optional[UUID4] = Field(
        None,
        description="Business UUID",
        example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    )
    type: OfferType = Field(
        ...,
        description="Offer Type",
    )

    status: BookingStatus = Field(
        ...,
        description="Booking Status",
    )
    is_instant_ticketing_required: bool = Field(
        True,
        description="Instant Ticketing Required",
    )
    last_ticketing_date: Optional[datetime] = Field(
        None,
        description="Last Ticketing Date",
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp",
    )
    segments: list[BookingSegment] = Field(
        ...,
        description="Segments",
    )
    passengers: list[BookingPassenger] = Field(
        ...,
        description="Passengers",
    )


class BookingResponse(Response):
    data: Booking = Field(
        ...,
        description="Booking",
    )
