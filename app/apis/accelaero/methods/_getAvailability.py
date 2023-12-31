from xml.etree import ElementTree
from ..utils.create_offer import create_offer
from app.schemas import Offer, FlightSearchRequest


def search(client, search_request: FlightSearchRequest) -> list[Offer]:
    request_data = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.opentravel.org/OTA/2003/05">
            <soapenv:Header>
                <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
                    <wsse:UsernameToken>
                        <wsse:Username>{client.key}</wsse:Username>
                        <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{client.secret}</wsse:Password>
                    </wsse:UsernameToken>
                </wsse:Security>
            </soapenv:Header>
            <soapenv:Body>
                <ns:OTA_AirAvailRQ Target="Production" Version="2006.01" DirectFlightsOnly="false">
                    <ns:POS>
                        <ns:Source TerminalID="{client.terminal_id}">
                            <ns:RequestorID Type="{client.requestor_id_type}" ID="{client.key}" />
                            <ns:BookingChannel Type="{client.booking_chanel}" />
                        </ns:Source>
                    </ns:POS>
                    <ns:OriginDestinationInformation>
                        <ns:DepartureDateTime>{search_request.departure_date}T00:00:00</ns:DepartureDateTime>
                        <ns:OriginLocation LocationCode="{search_request.origin}" CodeContext="IATA" />
                        <ns:DestinationLocation LocationCode="{search_request.destination}" CodeContext="IATA" />
                        <ns:TravelPreferences SmokingAllowed="false">
                            <ns:CabinPref PreferLevel="Preferred" Cabin="Y"/>
                        </ns:TravelPreferences>
                    </ns:OriginDestinationInformation>
                    <ns:TravelerInfoSummary>
                        <ns:AirTravelerAvail>
                            <ns:PassengerTypeQuantity Code="ADT" Quantity="{search_request.adult_count}"/>
                            <ns:PassengerTypeQuantity Code="CHD" Quantity="{search_request.child_count}"/>
                            <ns:PassengerTypeQuantity Code="INF" Quantity="{search_request.infant_count}"/>
                        </ns:AirTravelerAvail>
                    </ns:TravelerInfoSummary>
                </ns:OTA_AirAvailRQ>
            </soapenv:Body>
        </soapenv:Envelope>
        
    """

    # MAKING GET REQUEST FOR AVAIL FLIGHTS

    data = client.session.post(
        url=client.url,
        data=request_data,
        headers={"content-type": "text/xml"},
        timeout=client.search_timeout,
    )

    root = ElementTree.fromstring(data.content)

    OTA_AirAvailRS = root[0][0]

    errors = OTA_AirAvailRS.find(f"{client.BASE_SCHEMA_URL}Errors")

    for error in errors:
        print(error.text, error.attrib)

    quoted_itinerary = OTA_AirAvailRS.find(
        f".//{client.BASE_SCHEMA_URL}PricedItineraries"
    )

    if quoted_itinerary == None:
        return []

    quoted_option_info = quoted_itinerary.find(
        f".//{client.BASE_SCHEMA_URL}OriginDestinationOptions"
    )

    transaction_identifier = OTA_AirAvailRS.attrib.get("TransactionIdentifier")
    all_origin_destination_infos = OTA_AirAvailRS.findall(
        f"{client.BASE_SCHEMA_URL}OriginDestinationInformation"
    )

    for option in all_origin_destination_infos:
        options_info = option.find(
            f".//{client.BASE_SCHEMA_URL}OriginDestinationOptions"
        )
        if options_info == quoted_option_info:
            continue
        else:
            pass

    offer = create_offer(quoted_itinerary, client.BASE_SCHEMA_URL, client.id)

    return [offer]
