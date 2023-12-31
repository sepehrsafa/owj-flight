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
    Stop,
    FareRule,
    Details,
)
from owjcommon.enums import CurrencyChoices
from app.enums import OfferType, FareType, CabinType, DataSource, APIClient
from datetime import datetime
from xml.etree import ElementTree


def create_itineraries(xml, BASE_SCHEMA_URL):
    itineraries_list = []
    rphs = []
    for itinerary_id, itinerary in enumerate(xml):
        segments = itinerary.findall(f".//{BASE_SCHEMA_URL}FlightSegment")
        segments_list = []
        for segment_id, segment in enumerate(segments):
            departure_airport = segment.find(
                f"{BASE_SCHEMA_URL}DepartureAirport"
            ).attrib
            arrival_airport = segment.find(f"{BASE_SCHEMA_URL}ArrivalAirport").attrib
            segment_details = segment.attrib

            # breaking "W5$KER/SYZ/AWZ$543879$20231102051500$20231102083500"
            # into ["W5","KER/SYZ/AWZ","543879","20231102051500","20231102083500"]
            flight_ref = segment_details.get("RPH").split("$")

            rphs.append(segment_details.get("RPH"))

            _segments = flight_ref[1].split("/")

            stops_list = []

            if len(_segments) > 2:
                for stop in _segments[1:-1]:
                    stop = Stop(code=stop)
                    stops_list.append(stop)

            departure = Location(
                code=departure_airport.get("LocationCode"),
                at=segment_details.get("DepartureDateTime"),
                terminal=departure_airport.get("Terminal"),
            )

            arrival = Location(
                code=arrival_airport.get("LocationCode"),
                at=segment_details.get("ArrivalDateTime"),
                terminal=arrival_airport.get("Terminal"),
            )

            segment = Segment(
                code=flight_ref[1],
                departure=departure,
                arrival=arrival,
                flight_number=segment_details.get("FlightNumber"),
                operating_flight_number=segment_details.get("FlightNumber"),
                stop_count=int(segment_details.get("StopQuantity", 0)),
                stops=stops_list,
            )
            segments_list.append(segment)

        itinerary = Itinerary(
            segments=segments_list,
        )
        itineraries_list.append(itinerary)
    return itineraries_list, rphs


def create_fare(xml, BASE_SCHEMA_URL):
    pax_list = []

    for ptc in xml:
        base_fare = ptc.find(f".//{BASE_SCHEMA_URL}BaseFare").attrib
        total_fare = ptc.find(f".//{BASE_SCHEMA_URL}TotalFare").attrib
        taxes = ptc.findall(f".//{BASE_SCHEMA_URL}Tax")
        fees = ptc.findall(f".//{BASE_SCHEMA_URL}Fee")
        fare_infos = ptc.findall(f".//{BASE_SCHEMA_URL}FareInfo")
        quantity = ptc.find(f".//{BASE_SCHEMA_URL}PassengerTypeQuantity").attrib

        taxes_list = []
        for tax in taxes:
            _tax = tax.attrib
            taxes_list.append(
                Fee(
                    amount=_tax.get("Amount"),
                    code=_tax.get("TaxCode"),
                    name=_tax.get("TaxName"),
                )
            )

        fees_list = []
        for fee in fees:
            _fee = fee.attrib
            fees_list.append(
                Fee(
                    amount=_fee.get("Amount"),
                    code=_fee.get("FeeCode"),
                    name=_fee.get("FeeName"),
                )
            )

        pax_segment_list = []
        rules = []
        for segment_id, segment in enumerate(fare_infos):
            _segment = segment.attrib
            pax_segment_list.append(
                PaxSegment(
                    key=_segment.get("SegmentCode"),
                    cabin=CabinType.ECONOMY,
                    fare_basis=_segment.get("FareBasisCode"),
                    booking_class=_segment.get("FareBasisCode"),
                )
            )
            fare_info_rule = segment.find(f".//{BASE_SCHEMA_URL}FareRuleReference").text

            rules.append(
                FareRule(
                    code=_segment.get("SegmentCode"),
                    details=[
                        Details(
                            category="GENERAL",
                            text=fare_info_rule,
                        )
                    ],
                )
            )

        pax = Pax(
            type=quantity.get("Code"),
            count=int(quantity.get("Quantity")),
            segments=pax_segment_list,
            base=base_fare.get("Amount"),
            taxes=taxes_list,
            fees=fees_list,
            total=total_fare.get("Amount"),
            currency=CurrencyChoices.IRR,
            rules=rules,
        )

        pax_list.append(pax)

    fare = Fare(
        type=FareType.PUBLIC,
        number_of_seats=9,
        paxs=pax_list,
    )

    return fare


def create_offer(xml, BASE_SCHEMA_URL, api_id):
    itineraries = xml.findall(f".//{BASE_SCHEMA_URL}OriginDestinationOption")
    ptc_fare_breakdowns = xml.findall(f".//{BASE_SCHEMA_URL}PTC_FareBreakdown")

    fare_remark = xml.findall(f".//{BASE_SCHEMA_URL}Notes")

    final_remark = None

    for remark in fare_remark:
        if remark.text:
            if final_remark is None:
                final_remark = str(remark.text)
            else:
                final_remark += f"{remark.text}"

    itineraries_list, rphs_list = create_itineraries(itineraries, BASE_SCHEMA_URL)
    fare = create_fare(ptc_fare_breakdowns, BASE_SCHEMA_URL)

    rphs_string = "|".join(rphs_list)

    fare.key = (
        f"{api_id},{APIClient.ACCELAERO.value},{rphs_string},{CabinType.ECONOMY.value}"
    )

    fare.remarks = final_remark

    offer = Offer(
        type=OfferType.ONE_WAY,
        itineraries_source=DataSource.AIRLINE,
        itineraries=itineraries_list,
        fares=[fare],
    )
    return offer
