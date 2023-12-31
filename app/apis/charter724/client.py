import logging
from ..base import BaseConfig, BaseClient
from app.enums import APIClient
import base64
import requests
from app.schemas import FlightGridRequest, FlightSearchRequest
import datetime
from ._15_days import search as search_15_days
from ._available import search as search_available


class Charter724Client(BaseClient):
    __name__: str = APIClient.CHARTER724.value + "Client"
    client: APIClient = APIClient.CHARTER724

    def __init__(self, id, url, key, secret, extra, search_timeout):
        super().__init__(id, url, key, secret, extra, search_timeout)
        self.base64_username_password = self._get_base64_login()
        self.token_expire_time = None
        self.session = requests.Session()

    def get_search_cache_key(self, request: FlightGridRequest):
        return f"{self.client.value}:{self.id}:{request.departure_date}:{request.return_date}:{request.origin}:{request.destination}:{request.currency}"

    def grid_search(self, request: FlightGridRequest):
        # check request from_date to see if it is in 15 days range or not
        from_date = datetime.datetime.strptime(request.from_date, "%Y-%m-%d")
        today = datetime.datetime.today()
        fifteen_days = today + datetime.timedelta(days=15)
        # check if from_date is in 15 days range or not
        if from_date <= fifteen_days:
            self._check_token()
            return search_15_days(self, request)
        else:
            return []

    def search(self, request: FlightSearchRequest):
        self._check_token()
        return search_available(self, request)

    def validate(self, offer, fare):
        pass

    def fare_rules(fare_id):
        pass

    def fare_baggage(fare_id):
        pass

    def captcha(fare_id):
        pass

    def book(self):
        pass

    def issue(self):
        pass

    def _get_base64_login(self):
        self.logger.error(
            f"Getting base64 login for {self.client.value} with id {self.id}"
        )
        # concatenate username and password with a colon and base64 encode the result
        return base64.b64encode(bytes(self.key + ":" + self.secret, "utf-8")).decode(
            "ascii"
        )

    def _get_token(self):
        self.logger.error(f"Getting token for {self.client.value} with id {self.id}")
        print(self.base64_username_password)
        request = self.session.post(
            url=self.url + "/api/Login",
            json={"userPassBase64": f"Basic {self.base64_username_password}"},
        )
        if request.status_code != 200:
            self.logger.error(
                f"Error in getting token from {self.client.value} with status code {request.status_code} and response {request.text}"
            )
            return None

        response = request.json()
        if response["result"] == "true":
            self.session.headers.update(
                {"Authorization": "Bearer " + response["data"]["access_token"]}
            )
            # parse expire time in utc and convert to datetime
            self.token_expire_time = datetime.datetime.strptime(
                response["data"]["expires_Utc"][:23], "%Y-%m-%dT%H:%M:%S.%f"
            )
            self.logger.error(
                f"Token for {self.client.value} with id {self.id} is updated"
            )

    def _check_token(self):
        # temp
        """
        self.session.headers.update(
            {
                "Authorization": "Bearer "
                + "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjpbImNoYXJ0ZXJwYXJzZW93aiIsImNoYXJ0ZXIucGFyc2Vvd2oiXSwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIjoidXNlciIsInVzZXJuYW1lIjoiY2hhcnRlcnBhcnNlb3dqIiwiSWRfYWdhbmN5IjoiMTE1MTMiLCJJZHVzZXJfYWdhbmN5IjoiMzQ4NzEzIiwibW9kZV9hZ2FuY3kiOiJhY3RpdmUiLCJzaGFyZV9iYW5rIjoiMSIsImFjdGl2ZV92ZXJzaW9uIjoiMyIsIm5iZiI6MTY5NzU5NDg1MSwiZXhwIjoxNjk3NTk4NDUxLCJpc3MiOiJXZWJTZXJ2aWNlNzI0Q29yZSIsImF1ZCI6ImNsaWVudGNvbmVjdCJ9.e8zYMgSo0woY6siQspn0etS2OGBZ-yKiDYesClgJe1U"
            }
        )
        return
        """

        self.logger.error(f"Checking token for {self.client.value} with id {self.id}")
        if self.token_expire_time is None:
            self.logger.error(
                f"Token for {self.client.value} with id {self.id} is None"
            )
            self._get_token()
        else:
            if self.token_expire_time < datetime.datetime.utcnow() + datetime.timedelta(
                seconds=30
            ):
                self.logger.error(
                    f"Token for {self.client.value} with id {self.id} is expired"
                )
                self._get_token()
