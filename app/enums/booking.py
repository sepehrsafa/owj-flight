from enum import Enum


class BookingStatus(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    TICKETED = "TICKETED"
    PARTIALLY_CANCELLED = "PARTIALLY_CANCELLED"


class PassengerStatus(str, Enum):
    TICKETED = "TICKETED"
    CANCELLED = "CANCELLED"
    VOID = "VOID"
    UNKNOWN = "UNKNOWN"
