from app.enums import APIClient
from tortoise import fields

from owjcommon.enums import CurrencyChoices
from owjcommon.models import AuditableModel

from .audit import AuditLog


class APIs(AuditableModel):
    name = fields.CharField(max_length=100)
    site_url = fields.CharField(max_length=100, null=True, blank=True)
    is_active = fields.BooleanField(default=True)
    client = fields.CharEnumField(APIClient)

    url = fields.CharField(max_length=100)
    key = fields.CharField(max_length=100, null=True, blank=True)
    secret = fields.CharField(max_length=100, null=True, blank=True)
    extra = fields.JSONField(default={})

    allow_search_without_credit = fields.BooleanField(default=False)

    credit_available = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit_threshold = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit_currency = fields.CharEnumField(CurrencyChoices, default=CurrencyChoices.IRR)

    supported_currencies = fields.JSONField(default=[])
    preferred_currency = fields.CharEnumField(
        CurrencyChoices, default=CurrencyChoices.IRR
    )

    support_roundtrip = fields.BooleanField(default=False)
    support_city_search = fields.BooleanField(default=False)

    allow_pax_count_in_cache_key = fields.BooleanField(default=False)
    search_cache_time = fields.IntField(default=0)
    search_timeout = fields.IntField(default=0)

    audit_log_class = AuditLog

    class Meta:
        table = "flight_apis"
