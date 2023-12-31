from apps.flights.choices import CabinTypeChoices
from apps.accounts.choices import PaxTypeChoices, TitleTypeChoices


class PaxTypeChoicesMap:

    map = {
        'Adult(s)': PaxTypeChoices.ADULT,
        'Children': PaxTypeChoices.CHILD,
        'Infant(s)': PaxTypeChoices.INFANT,
        'ADT': PaxTypeChoices.ADULT,
        'CHD': PaxTypeChoices.CHILD,
        'INF': PaxTypeChoices.INFANT,
        'AD': PaxTypeChoices.ADULT,
        'CH': PaxTypeChoices.CHILD,
        'BABY': PaxTypeChoices.INFANT,
    }

    @staticmethod
    def get(passenger_type):
        return PaxTypeChoicesMap.map.get(passenger_type)


class CabinClassChoicesMap:

    map = {
        'Y': CabinTypeChoices.ECONOMY,
        'A': CabinTypeChoices.PREMIUM_ECONOMY,
        'C': CabinTypeChoices.BUSINESS,
    }

    @staticmethod
    def get(cabin_class):
        return CabinClassChoicesMap.map.get(cabin_class)

    @staticmethod
    def to(cabin_class):
        keys = [key for key, value in CabinClassChoicesMap.map.items()
                if value == cabin_class]
        return keys[0]


class TitleTypeChoicesMap:

    map = {
        "MR": TitleTypeChoices.MR,
        "MRS": TitleTypeChoices.MRS,
        "MS": TitleTypeChoices.MS,
        "MISS": TitleTypeChoices.MISS,
        'MSTR': TitleTypeChoices.MISTER,
    }

    @staticmethod
    def get(title_type):
        return TitleTypeChoicesMap.map.get(title_type)

    @staticmethod
    def to(title_type):
        keys = [key for key, value in TitleTypeChoicesMap.map.items()
                if value == title_type]
        return keys[0]
