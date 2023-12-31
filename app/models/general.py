from app.enums import APIClient
from tortoise import fields

from owjcommon.enums import CurrencyChoices
from owjcommon.models import AuditableModel

from .audit import AuditLog
from functools import lru_cache


class City(AuditableModel):
    name_fa = fields.CharField(max_length=100)
    name_en = fields.CharField(max_length=100)
    iata_code = fields.CharField(max_length=3, unique=True, index=True)
    icao_code = fields.CharField(max_length=4, null=True)
    country_code = fields.CharField(max_length=2)
    audit_log_class = AuditLog

    class Meta:
        table = "flight_city"


class Airport(AuditableModel):
    name_fa = fields.CharField(max_length=100)
    name_en = fields.CharField(max_length=100)
    iata_code = fields.CharField(max_length=3, unique=True, index=True)
    icao_code = fields.CharField(max_length=4, null=True)
    city = fields.ForeignKeyField(
        "models.City", related_name="airports", to_field="iata_code"
    )

    async def get_all_airports():
        return await Airport.all().prefetch_related("city")

    audit_log_class = AuditLog

    class Meta:
        table = "flight_airport"


class Airline(AuditableModel):
    name_fa = fields.CharField(max_length=100)
    name_en = fields.CharField(max_length=100)
    iata_code = fields.CharField(max_length=3, unique=True, index=True)
    icao_code = fields.CharField(max_length=4, null=True)
    charter724_name = fields.CharField(max_length=100, null=True)
    parto_name = fields.CharField(max_length=100, null=True)

    audit_log_class = AuditLog

    class Meta:
        table = "flight_airline"
