from pydantic import UUID4, BaseModel, Field, conint, model_validator, validator

from owjcommon.schemas import Response, PaginatedResult, Filters
from tortoise.contrib.pydantic import pydantic_model_creator
from app.models import Airline as AirlineModel
from app.models import Airport as AirportModel
from app.models import City as CityModel
from datetime import datetime
from typing import Union, Optional

AirlineRequest = pydantic_model_creator(
    AirlineModel, exclude=("id", "created_at", "updated_at"), name="AirlineRequest"
)
AirportBaseRequest = pydantic_model_creator(
    AirportModel, exclude=("id", "created_at", "updated_at"), name="AirportRequest"
)
CityRequest = pydantic_model_creator(
    CityModel, exclude=("id", "created_at", "updated_at"), name="CityRequest"
)


class CityFilters(Filters):
    name_fa: Optional[str] = Field(None, description="Name in Persian", example="تهران")
    name_en: Optional[str] = Field(
        None, description="Name in English", example="Tehran"
    )
    iata_code: Optional[str] = Field(None, description="IATA Code", example="THR")
    icao_code: Optional[str] = Field(None, description="ICAO Code", example="OIII")
    country_code: Optional[str] = Field(None, description="Country Code", example="IR")


Airline = pydantic_model_creator(AirlineModel, name="Airline")


class AirlineFilters(Filters):
    name_fa: Optional[str] = Field(
        None, description="Name in Persian", example="ایران ایر"
    )
    name_en: Optional[str] = Field(
        None, description="Name in English", example="Iran Air"
    )
    iata_code: Optional[str] = Field(None, description="IATA Code", example="IR")
    icao_code: Optional[str] = Field(None, description="ICAO Code", example="IRA")
    charter724_name: Optional[str] = Field(
        None, description="Charter724 Name", example="ایران ایر"
    )
    parto_name: Optional[str] = Field(
        None, description="Parto Name", example="ایران ایر"
    )


AirportBase = pydantic_model_creator(AirportModel, name="Airport")
City = pydantic_model_creator(CityModel, name="City")


class AirportRequest(AirportBaseRequest):
    city_iata_code: Union[str, None] = Field(
        None, description="City IATA Code", example="THR"
    )
    city_uuid: Union[UUID4, None] = Field(
        None, description="City UUID", example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    )

    # check if city_uuid or city_iata_code is provided
    @validator("city_uuid")
    def city_uuid_or_city_iata_code(cls, v, values, **kwargs):
        if v is None and values.get("city_iata_code") is None:
            raise ValueError("Either city_uuid or city_iata_code must be provided")
        return v


class Airport(AirportBase):
    city: City


class AirlineResponse(Response):
    data: Airline


class AirlinesResponse(PaginatedResult):
    items: list[Airline]


class AirportResponse(Response):
    data: Airport


class AirportsResponse(PaginatedResult):
    items: list[Airport]


class CityResponse(Response):
    data: City


class CitiesResponse(PaginatedResult):
    items: list[City]


class SearchCacheItem(BaseModel):
    search_key: str
    been_fetched: bool = False
    api_id: int
    latest_known_celery_task_id: str
    latest_know_celery_task_id_expiry_utc: datetime


class SearchCache(BaseModel):
    items: list[SearchCacheItem]
    search_track_id: str
    has_all_tasks_finished: bool = False
