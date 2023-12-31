from app.enums import APIClient, BookingStatus, CabinType, FareType, PassengerStatus
from tortoise import fields

from owjcommon.enums import CountryChoices, CurrencyChoices
from owjcommon.models import AuditableModel

from .audit import AuditLog


class Booking(AuditableModel):
    user = fields.UUIDField()
    business = fields.UUIDField(null=True)
    type = fields.CharEnumField(FareType, default=FareType.UNKNOWN)
    currency = fields.CharEnumField(CurrencyChoices, default=CurrencyChoices.IRR)
    status = fields.CharEnumField(BookingStatus)
    is_instant_ticketing_required = fields.BooleanField(default=True)
    last_ticketing_date = fields.DatetimeField(null=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    api = fields.ForeignKeyField("models.APIs", related_name="bookings")

    audit_log_class = AuditLog

    class Meta:
        ordering = ["-id"]
        table = "flight_booking"

    # total
    # refund_total
    # passengers
    # segments


class Passenger(AuditableModel):
    first_name = fields.CharField(max_length=250)
    last_name = fields.CharField(max_length=250)
    date_of_birth = fields.DateField(null=True)
    iran_national_id = fields.CharField(max_length=10, null=True)
    passport_number = fields.CharField(max_length=20, null=True)
    passport_expiry_date = fields.DateField(null=True)
    passport_issue_date = fields.DateField(null=True)
    passport_issuance_country = fields.CharEnumField(
        CountryChoices, default=CountryChoices.IR
    )

    base = fields.DecimalField(max_digits=10, decimal_places=2)
    tax = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    fee = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    service = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    markup = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = fields.DecimalField(max_digits=10, decimal_places=2)
    currency = fields.CharEnumField(CurrencyChoices, default=CurrencyChoices.IRR)
    penalty = fields.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_total = fields.DecimalField(max_digits=10, decimal_places=2, default=0)

    timestamp = fields.DatetimeField(auto_now_add=True)

    booking = fields.ForeignKeyField("models.booking", related_name="passengers")

    audit_log_class = AuditLog

    class Meta:
        ordering = ["-id"]
        table = "flight_passenger"


class PassengerSegment(AuditableModel):
    status = fields.CharEnumField(PassengerStatus, default=PassengerStatus.UNKNOWN)
    pnr = fields.CharField(max_length=20, null=True)
    ticket_number = fields.CharField(max_length=50, null=True)
    cabin = fields.CharEnumField(CabinType, default=CabinType.ECONOMY)
    fare_basis = fields.CharField(max_length=20)
    booking_class = fields.CharField(max_length=20)
    branded_fare = fields.CharField(max_length=100, null=True)
    baggage = fields.CharField(max_length=50, null=True)
    carryon = fields.CharField(max_length=50, null=True)
    booking = fields.ForeignKeyField(
        "models.Booking", related_name="passenger_segments"
    )
    passenger = fields.ForeignKeyField(
        "models.Passenger", related_name="passenger_segments"
    )
    segment = fields.ForeignKeyField(
        "models.Segment", related_name="passenger_segments"
    )

    audit_log_class = AuditLog

    class Meta:
        ordering = ["-id"]
        table = "flight_passenger_segment"


class Stop(AuditableModel):
    airport = fields.ForeignKeyField("models.Airport", related_name="stops")
    arrival = fields.CharField(max_length=100, null=True)
    departure = fields.CharField(max_length=100, null=True)
    segment = fields.ForeignKeyField("models.Segment", related_name="stops")

    audit_log_class = AuditLog

    class Meta:
        ordering = ["-id"]
        table = "flight_stop"


class Segment(AuditableModel):
    code = fields.CharField(max_length=50)
    origin = fields.ForeignKeyField(
        "models.Airport", related_name="segments_origin", to_field="iata_code"
    )
    destination = fields.ForeignKeyField(
        "models.Airport", related_name="segments_destination", to_field="iata_code"
    )
    departure = fields.DatetimeField()
    arrival = fields.DatetimeField()
    flight_number = fields.CharField(max_length=10)
    operating_flight_number = fields.CharField(max_length=10)
    airline = fields.ForeignKeyField(
        "models.Airline",
        related_name="segments",
        to_field="iata_code",
    )
    operating_airline = fields.ForeignKeyField(
        "models.Airline",
        related_name="operating_segments",
        to_field="iata_code",
    )
    aircraft = fields.CharField(max_length=40, null=True)
    remarks = fields.TextField(null=True)
    booking = fields.ForeignKeyField("models.Booking", related_name="segments")

    audit_log_class = AuditLog

    class Meta:
        ordering = ["-id"]
        table = "flight_segment"


class Note(AuditableModel):
    audit_log_class = AuditLog
    text = fields.TextField()
    user = fields.UUIDField()
    booking = fields.ForeignKeyField("models.Booking", related_name="notes")
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        table = "flight_note"
