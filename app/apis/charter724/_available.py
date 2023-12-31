from app.schemas import (
    FlightSearchRequest,
    Offer,
    Fare,
    Pax,
    Fee,
    PaxSegment,
    Itinerary,
    Segment,
    Location,
)
from owjcommon.enums import CurrencyChoices
from .utils import convert_fare_type, convert_cabin_type
from app.enums import OfferType, FareType, CabinType, DataSource, APIClient
from datetime import datetime


def search(client, search_request: FlightSearchRequest):
    END_POINT = "/api/WebService/Available"
    client.logger.error(
        f"Searching flights with {client.client.value} with id {client.id} for {search_request.origin} to {search_request.destination} for {search_request.departure_date}"
    )
    request = client.session.post(
        client.url + END_POINT,
        json={
            "from_flight": search_request.origin,
            "to_flight": search_request.destination,
            "date_flight": search_request.departure_date
        },
    )
    if request.status_code != 200:
        client.logger.error(
            f"Error in getting data in {END_POINT} from {client.client.value} with status code {request.status_code} and response {request.text}"
        )
        return []

    response = request.json()

    available_flights_map = {}

    available_offers = []

    for flight in response.get("data", []):
        _origin = Location(
            code=flight["from"],
            at=f'{flight["date_flight"]}T{flight["time_flight"]}',
        )
        _destination = Location(
            code=flight["to"],
        )

        _fare_type = convert_fare_type(flight["type"])
        _flight_number = flight["number_flight"].upper()
        _airline_code = flight["iatA_code"].upper()

        # if airline code is part of flight number, remove it
        _flight_number = _flight_number.replace(_airline_code, "")
        if _fare_type == FareType.CHARTER:
            # if ch is part of flight number, remove it
            _flight_number = _flight_number.replace("CH", "")

        #if last character of flight number is C, remove it
        if _flight_number[-1] == "C":
            _flight_number = _flight_number[:-1]

        _aircraft = flight["carrier"]

        if _aircraft.lower() == "unknow":
            _aircraft = None

        _cabin = convert_cabin_type(flight["type_flight"])

        if (_aircraft == "BAE 146" and _airline_code == "W5" and _cabin == CabinType.BUSINESS):
            continue

        _segment = Segment(
            code=f"{_origin.code}/{_destination.code}",
            departure=_origin,
            arrival=_destination,
            flight_number=_airline_code+_flight_number,
            operating_flight_number=_airline_code+_flight_number,
            aircraft=_aircraft,
            remarks=flight["alarm_msg"],
            stop_count=flight["has_stop"],
        )

        _itinerary = Itinerary(
            segments=[_segment],
        )

        _fare_basis = flight["cabinclass"].upper()
        
        _pax_segment = PaxSegment(
            key=_segment.key,
            cabin=_cabin,
            fare_basis=_fare_basis,
            booking_class=_fare_basis,
        )

        _adult_pax = Pax(
            type="ADT",
            segments=[_pax_segment],
            base=flight["price_final_fare"],
            tax=Fee(
                amount=flight["price_final"] - flight["price_final_fare"],
                name="TAX",
                code="TAX",
            ),
            total=flight["price_final"],
            currency=CurrencyChoices.IRR,
        )

        _fare = Fare(
            key= f"{APIClient.CHARTER724.value},{flight.get('ajency_online_ID')}",
            type=_fare_type,
            number_of_seats=flight["capacity"],
            is_refundable=None,
            is_exchangable=None,
            instant_ticketing_required=True,
            paxs=[_adult_pax],
        )

        # check available_flights_map
        if _itinerary.key in available_flights_map:
            _data = available_flights_map[_itinerary.key]
            if (
                not _data["is_itinerary_from_public_result"]
                and _fare_type == FareType.PUBLIC
            ):
                # update itinerary
                _data["itinerary"] = _itinerary
                _data["is_itinerary_from_public_result"] = True
                # append fare
            _data["offers"].append(_fare)

        else:
            available_flights_map[_itinerary.key] = {
                "is_itinerary_from_public_result": True
                if _fare_type == FareType.PUBLIC
                else False,
                "itinerary": _itinerary,
                "offers": [_fare],
            }

    for data in available_flights_map.values():
        print(data)
        available_offers.append(
            Offer(
                type=OfferType.ONE_WAY,
                itineraries=[data["itinerary"]],
                fares=data["offers"],
                itineraries_source=DataSource.THIRD_PARTY
            )
        )

    return available_offers
