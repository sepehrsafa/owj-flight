from typing import Optional

from app.config import settings
from app.enums import CabinType, IATACodeType
from pydantic import UUID4, BaseModel, Field, conint, model_validator, validator

from owjcommon.enums import CurrencyChoices
from owjcommon.schemas import Response
from .offer import Offer


class FlightSearchRequest(BaseModel):
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
    departure_date: str = Field(
        ...,
        description="Departure date in YYYY-MM-DD format",
        serialization_alias="departureDate",
        example="2023-12-30",
    )
    return_date: Optional[str] = Field(
        None,
        description="Return date in YYYY-MM-DD format",
        serialization_alias="returnDate",
        example="2023-12-31",
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
    adult_count: conint(ge=1, le=9) = Field(
        1,
        description="Number of adults",
        validation_alias="adultCount",
    )
    child_count: conint(ge=0, le=8) = Field(
        0,
        description="Number of children",
        validation_alias="childCount",
    )
    infant_count: conint(ge=0, le=4) = Field(
        0,
        description="Number of infants",
        validation_alias="infantCount",
    )
    allow_one_way_offers: bool = Field(
        True,
        description="Allow one way offers",
        validation_alias="allowOneWayOffers",
    )

    """
    @model_validator(mode="after")
    def check_model(self):
        # class validator to check total number of passengers is less than 9
        if self.adult_count + self.child_count + self.infant_count > 9:
            raise ValueError("Total number of passengers cannot be more than 9")

        # model validator to check if infant count is less than or equal to adult count
        if self.infant_count > self.adult_count:
            raise ValueError("Number of infants cannot be more than number of adults")
    """


class FlightSearchResponse(Response):
    search_id: UUID4 = Field(
        ...,
        description="Flight search ID",
        serialization_alias="searchId",
        example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    )
    timeout: int = Field(
        settings.search.timeout,
        description="Time in seconds after which search you can get results",
    )
    is_finished: bool = Field(
        False,
        description="Is search finished",
        serialization_alias="isFinished",
    )
    offers: list[Offer] = Field(
        default_factory=list,
        description="List of offers",
    )
