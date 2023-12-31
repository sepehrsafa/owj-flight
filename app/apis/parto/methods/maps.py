from apps.flights.choices import FareTypeChoices, CabinTypeChoices
from apps.accounts.choices import GenderTypeChoices, PaxTypeChoices,TitleTypeChoices


class FareTypeChoicesMap:

    map = {
        1: FareTypeChoices.PUBLIC,
        2: FareTypeChoices.PUBLIC,
        3: FareTypeChoices.PRIVATE,
        4: FareTypeChoices.WEB,
        6: FareTypeChoices.CORPORATE,
        7: FareTypeChoices.CORPORATE,
        10: FareTypeChoices.NET,
        20: FareTypeChoices.CHARTER,
    }

    @staticmethod
    def get(fare_type):
        return FareTypeChoicesMap.map.get(fare_type, FareTypeChoices.PUBLIC)

    @staticmethod
    def to(fare_type):
        keys = [key for key, value in FareTypeChoicesMap.map.items() if value == fare_type]
        return keys[0]


class PaxTypeChoicesMap:

    map = {
        1: PaxTypeChoices.ADULT,
        2: PaxTypeChoices.CHILD,
        3: PaxTypeChoices.INFANT,
    }

    @staticmethod
    def get(passenger_type):
        return PaxTypeChoicesMap.map.get(passenger_type)

    @staticmethod
    def to(passenger_type):
        keys = [key for key, value in PaxTypeChoicesMap.map.items() if value == passenger_type]
        return keys[0]


class CabinClassChoicesMap:

    map = {
        1: CabinTypeChoices.ECONOMY,
        2: CabinTypeChoices.PREMIUM_ECONOMY,
        3: CabinTypeChoices.BUSINESS,
        4: CabinTypeChoices.PREMIUM_BUSINESS,
        5: CabinTypeChoices.FIRST,
        6: CabinTypeChoices.PREMIUM_FIRST,
    }

    @staticmethod
    def get(cabin_class):
        return CabinClassChoicesMap.map.get(cabin_class)

    @staticmethod
    def to(cabin_class):
        keys = [key for key, value in CabinClassChoicesMap.map.items() if value == cabin_class]
        return keys[0]


class GenderTypeChoicesMap:

    map = {
        0: GenderTypeChoices.M,
        1: GenderTypeChoices.F,
    }

    @staticmethod
    def get(gender_type):
        return GenderTypeChoicesMap.map.get(cabin_class)

    @staticmethod
    def to(gender_type):
        keys = [key for key, value in GenderTypeChoicesMap.map.items() if value == gender_type]
        return keys[0]


class TitleTypeChoicesMap:

    map = {
        0: TitleTypeChoices.MR,
        1: TitleTypeChoices.MRS,
        2: TitleTypeChoices.MS,
        3: TitleTypeChoices.MISS,
        4: TitleTypeChoices.MISTER,
    }

    @staticmethod
    def get(title_type):
        return TitleTypeChoicesMap.map.get(title_type)

    @staticmethod
    def to(title_type):
        keys = [key for key, value in TitleTypeChoicesMap.map.items() if value == title_type]
        return keys[0]