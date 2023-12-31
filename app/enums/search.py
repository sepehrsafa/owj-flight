from enum import Enum


class IATACodeType(str, Enum):
    AIRPORT = "AIRPORT"
    CITY = "CITY"


class CabinType(str, Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"


class FareType(str, Enum):
    PUBLIC = "PUBLIC"
    CHARTER = "CHARTER"
    UNKNOWN = "UNKNOWN"


class OfferType(str, Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class DataSource(str, Enum):
    AIRLINE = "AIRLINE"
    THIRD_PARTY = "THIRD_PARTY"
