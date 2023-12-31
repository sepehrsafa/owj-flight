from dataclasses import dataclass, field
from typing import List





@dataclass
class AccelAeroFlightRPH:
    flight_rph: str 
    departure_time_zulu: str = field(default=None)


@dataclass
class AccelAeroSourceInfo:
    flight_refs: List[AccelAeroFlightRPH] = field(default=None)
    adult_count: int = field(default=None)
    child_count: int = field(default=None)
    infant_count: int = field(default=None)
    cabin_of_service: str = field(default=None)
    origin: str = field(default=None)
    destination: str = field(default=None)
    departure_date: str = field(default=None)
    return_date: str = field(default=None)

    def add_flight_rph(self, flight_rph: AccelAeroFlightRPH):
        self.flight_refs.append(flight_rph)

    def get_copy(self):
        return AccelAeroSourceInfo(
            flight_refs=[],
            adult_count=self.adult_count,
            child_count=self.child_count,
            infant_count=self.infant_count,
            cabin_of_service=self.cabin_of_service,
            origin=self.origin,
            destination=self.destination,
            departure_date=self.departure_date,
            return_date=self.return_date
        )
