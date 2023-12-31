from typing import Optional

from .validate import Passenger
from pydantic import UUID4, BaseModel, EmailStr, Field, model_validator, validator


class FlightBookFareKey(BaseModel):
    key: str = Field(
        ...,
        description="Fare Key",
        example="1234567890",
    )
    captcha: Optional[str] = Field(
        ...,
        description="Captcha",
        example="1234567890",
    )


class FlightBookRequest(BaseModel):
    search_id: UUID4 = Field(
        ...,
        description="Search ID",
        example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    )
    fares: list[FlightBookFareKey] = Field(
        ...,
        description="List of Fare Keys",
    )
    passengers: list[Passenger] = Field(
        ...,
        description="List of Passengers",
    )
    phone_number: str = Field(
        ...,
        description="Phone Number",
        example="09123456789",
    )
    email: EmailStr = Field(
        ...,
        description="Email",
        example="sepehr@owj.app",
    )
