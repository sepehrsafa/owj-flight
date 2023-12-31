from app.schemas import FlightGridRequest, FlightGridData
from owjcommon.enums import CurrencyChoices
from .utils import convert_fare_type
from datetime import datetime


def search(self, search_request: FlightGridRequest):
    self.logger.error(
        f"Searching next 15 days with {self.client.value} with id {self.id} for {search_request.origin} to {search_request.destination} from {search_request.from_date} to {search_request.to_date}"
    )
    request = self.session.post(
        self.url + "/api/WebService/Available15Days",
        json={
            "from_flight": search_request.origin,
            "to_flight": search_request.destination,
        },
    )
    if request.status_code != 200:
        self.logger.error(
            f"Error in getting /api/WebService/Available15Days from {self.client.value} with status code {request.status_code} and response {request.text}"
        )
        return []

    response = request.json()

    available_flights = []

    for flight in response.get("data", []):
        if flight["capacity"] == 0:
            continue

        # check if date_flight is passed to_date or not
        if datetime.strptime(flight["date_flight"], "%Y-%m-%d") > datetime.strptime(
            search_request.to_date, "%Y-%m-%d"
        ):
            continue

        commission = flight["share_Sale"]
        if commission <= 0:
            commission = None

        available_flights.append(
            FlightGridData(
                departure_date=flight["date_flight"],
                price=flight["price_final"],
                currency=CurrencyChoices.IRR,
                airline=flight["iatA_code"],
                commission=commission,
                type=convert_fare_type(flight["type"]),
            )
        )
    return available_flights
