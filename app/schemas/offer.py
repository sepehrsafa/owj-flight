from datetime import datetime
from decimal import Decimal
from typing import Optional, Union

from app.config import settings
from app.enums import CabinType, DataSource, IATACodeType, OfferType
from pydantic import UUID4, BaseModel, Field, conint, root_validator, validator

from owjcommon.enums import CurrencyChoices
from owjcommon.schemas import Password, Response


class Location(BaseModel):
    code: str = Field(
        ...,
        description="Location code",
        example="THR",
    )
    at: Union[str, None] = Field(
        None,
        description="Departure/Arrival time",
        example="2023-12-30T12:00:00",
    )
    terminal: Union[str, None] = Field(
        None,
        description="Terminal",
        example="A12",
    )


class Stop(BaseModel):
    arrival: Union[str, None] = Field(
        None,
        description="Departure/Arrival time",
        example="2023-12-30T12:00:00",
    )
    departure: Union[str, None] = Field(
        None,
        description="Departure/Arrival time",
        example="2023-12-30T12:00:00",
    )

    code: str = Field(
        ...,
        description="Location code",
        example="THR",
    )

    terminal: Union[str, None] = Field(
        None,
        description="Terminal",
        example="A12",
    )

    duration: Union[str, None] = Field(
        None,
        description="Duration",
        duration="PT2H30M",
    )


class Segment(BaseModel):
    key: str = Field(
        ...,
        description="Segment key. Segment key is a combination of departure code, arrival code, airline and flight number.",
        example="THR/MHD/TK1024/TK1025",
    )
    code: str = Field(
        ...,
        description="Segment code. Segment code is a combination of departure code, arrival code and stops.",
        example="THR/KER/MHD",
    )
    departure: Location = Field(
        ...,
        description="Departure location",
    )
    arrival: Location = Field(
        ...,
        description="Arrival location",
    )
    flight_number: str = Field(
        ...,
        description="Flight number, first two characters are airline code and the rest is flight number",
        example="TK1024",
    )
    operating_flight_number: str = Field(
        ...,
        description="Operating flight number, first two characters are airline code and the rest is flight number",
        example="TK1025",
    )
    duration: Union[str, None] = Field(
        None,
        description="Duration",
        duration="PT2H30M",
    )
    aircraft: Union[str, None] = Field(
        None,
        description="Aircraft",
        example="A320",
    )
    remarks: Union[str, None] = Field(
        None,
        description="Remarks",
        example="This flight is ......",
    )
    stop_count: int = Field(
        0,
        description="Stop count",
        example=2,
    )
    stops: Union[list[Stop], None] = Field(
        default_factory=list,
        description="List of stops",
    )

    @root_validator(pre=True)
    def set_key(cls, values):
        if values.get("key") is None:
            values[
                "key"
            ] = f"{values['departure'].code}/{values['arrival'].code}/{values['flight_number']}/{values['operating_flight_number']}"
        return values


class Itinerary(BaseModel):
    key: str = Field(..., description="Itinerary key", example="THR")

    duration: Union[str, None] = Field(
        None,
        description="Itinerary duration",
    )
    segments: list[Segment] = Field(
        ...,
        description="List of segments",
    )

    @root_validator(pre=True)
    def set_key(cls, values):
        if values.get("key") is None:
            values["key"] = "$".join([segment.key for segment in values["segments"]])
        return values


class Details(BaseModel):
    category: Union[str, None] = Field(
        None,
        description="Category",
        example="Penalty",
    )
    text: Union[str, None] = Field(
        None,
        description="Text",
        example="Penalty",
    )


class FareRule(BaseModel):
    code: str = Field(
        ...,
        description="City pair code",
        example="THR/IST",
    )
    details: list[Details] = Field(
        ...,
        description="List of details",
    )


class PaxSegment(BaseModel):
    key: str = Field(
        ...,
        description="Segment key",
    )
    cabin: CabinType = Field(
        ...,
        description="Cabin type",
        example=CabinType.ECONOMY,
    )
    fare_basis: str = Field(
        ...,
        description="Fare basis",
        example="Y",
    )
    booking_class: str = Field(
        ...,
        description="Booking class",
        example="Y",
    )
    branded_fare: Union[str, None] = Field(
        None,
        description="Branded fare",
        example="Y",
    )
    baggage: Union[str, None] = Field(
        None,
        description="Baggage",
        example="2 PC",
    )
    carryon: Union[str, None] = Field(
        None,
        description="Carryon",
        example="8 KG",
    )


class Fee(BaseModel):
    amount: Decimal = Field(
        ...,
        description="Fee amount",
        example=1000000,
    )
    name: Union[str, None] = Field(
        ...,
        description="Fee name",
        example="Taxes",
    )
    code: Union[str, None] = Field(
        ...,
        description="Fee code",
        example="TAX",
    )


class Pax(BaseModel):
    type: str = Field(
        ...,
        description="PAX type",
        example="ADT",
    )
    count: Union[int, None] = Field(
        None,
        description="PAX count",
        example=1,
    )
    segments: list[PaxSegment] = Field(
        ...,
        description="List of segments",
    )
    base: Decimal = Field(
        ...,
        description="Base fare",
        example=1000000,
    )
    taxes: list[Fee] = Field(
        default_factory=list,
        description="List of taxes",
    )
    fees: list[Fee] = Field(
        default_factory=list,
        description="List of fees",
    )
    services: list[Fee] = Field(
        default_factory=list,
        description="List of services",
    )
    discounts: list[Fee] = Field(
        default_factory=list,
        description="List of discounts",
    )
    total: Decimal = Field(
        ...,
        description="Total fare",
        example=1000000,
    )
    currency: CurrencyChoices = Field(
        ...,
        description="Currency",
        example=CurrencyChoices.IRR,
    )
    rules: list[FareRule] = Field(
        default_factory=list,
        description="List of fare rules",
    )


class Fare(BaseModel):
    key: Union[str, None] = Field(
        None,
        description="Fare key",
    )
    priority: int = Field(
        0,
        description="Fare priority",
        example=1,
    )
    type: str = Field(
        ...,
        description="Fare type",
    )
    number_of_seats: int = Field(
        ...,
        description="Number of seats",
        example=1,
    )
    is_refundable: Union[bool, None] = Field(
        None,
        description="Is refundable",
        example=True,
    )
    is_exchangeable: Union[bool, None] = Field(
        None,
        description="Is changeable",
        example=True,
    )
    instant_ticketing_required: bool = Field(
        True,
        description="Instant ticketing required",
        example=True,
    )
    last_ticketing_date: Union[str, None] = Field(
        None,
        description="Last ticketing date",
    )
    paxs: list[Pax] = Field(
        ...,
        description="List of paxs",
    )
    remarks: Union[str, None] = Field(
        None,
        description="Remarks",
        example="This fare is ......",
    )


class Offer(BaseModel):
    type: OfferType = Field(
        ...,
        description="Offer type",
        example=OfferType.ONE_WAY,
    )

    itineraries_source: DataSource = Field(
        ...,
        description="Itineraries source",
        example=DataSource.AIRLINE,
    )

    key: str = Field(
        ...,
        description="Offer key",
        example="THR$MHD$TK1024$TK1025",
    )

    itineraries: list[Itinerary] = Field(
        ...,
        description="List of itineraries",
    )
    fares: Optional[list[Fare]] = Field(
        None,
        description="List of fares",
    )
    fare: Optional[Fare] = Field(
        None,
        description="Single fare, this is the fare that will be used for booking",
    )
    captcha_link: Optional[str] = Field(
        None,
        description="Captcha Link",
    )

    @root_validator(pre=True)
    def set_key(cls, values):
        if values.get("key") is None:
            values["key"] = "|".join(
                [itinerary.key for itinerary in values["itineraries"]]
            )
        return values


class FlightSearchDataResponse(Response):
    is_finished: bool = Field(
        ...,
        description="Is search finished",
        example=True,
    )
    timeout: int = Field(
        ...,
        description="Timeout",
        example=3000,
    )

    offers: list[Offer] = Field(
        ...,
        description="List of offers",
    )
