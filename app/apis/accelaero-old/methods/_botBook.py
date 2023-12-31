import json

from apps.accounts.choices import DocumentTypeChoices, PaxTypeChoices

from .maps import TitleTypeChoicesMap


class Book:
    def __init__(self, client):
        self.client = client
        self.config = client.config
        self.airline = self.config.airline

    @staticmethod
    def datetime_to_string(data):
        '''
        Convert date and time from string to datetime object
        '''
        return data.strftime('%d/%m/%Y')



    def ancillary_block(self, pax_details, selected_flight_list):

        data = {
            'searchParams.departureDate': self.datetime_to_string(self.source_info.departure_date),
            'searchParams.returnDate': '',
            'searchParams.classOfService': self.source_info.cabin_of_service,
            'searchParams.bookingType': 'NORMAL',
            'searchParams.allowOverrideSameOrHigherFare': 'false',
            'selectedFlightList': json.dumps(selected_flight_list),
            'paxWiseAnci': json.dumps(pax_details),
        }

       
        status, text, headers = self.config.post_form('xbe/private/anciBlocking.action', data=data)



    def confirmation_tab(self, pax_adults, pax_infants, selected_flight_list, email, phone_number):

        phone_number_as_e164 = phone_number.as_e164
        #remove + from phone number using replace
        phone_number_as_e164 = phone_number_as_e164.replace('+', '')
        #remove country code from phone number
        phone_number_as_e164 = phone_number_as_e164[len(str(phone_number.country_code)):]
        area_code = phone_number_as_e164[0:3]
        number = phone_number_as_e164[3:]
        

        data = {

            'contactInfo.title': 'MR',
            'contactInfo.firstName': 'Sepehr',
            'contactInfo.lastName': 'Safa',
            'contactInfo.mobileCountry': str(phone_number.country_code),
            'contactInfo.mobileArea': area_code,
            'contactInfo.mobileNo': number,
            'contactInfo.phoneCountry': '',
            'contactInfo.phoneArea': '',
            'contactInfo.phoneNo': '',
            'contactInfo.faxCountry': str(phone_number.country_code),
            'contactInfo.faxArea': '',
            'contactInfo.faxNo': '',
            'contactInfo.city': 'KER',
            'contactInfo.email': email,
            'contactInfo.userNotes': 'Booked by Parse Computer Reservation System (CRS)',
            'contactInfo.country': 'IR',
            'selBookingCategory': 'STD',
            'paxAdults': json.dumps(pax_adults),
            'paxInfants': json.dumps(pax_infants),
            'onHoldBooking': 'true',
            'paxPayments': '[]',
            'payment.amount': '0.00',
            'payment.type': 'ACCO',
            'payment.amountWithCharge': '0',
            'payment.agent': 'KER28',
            'selectedFlightList': json.dumps(selected_flight_list),
            'selectedBookingCategory': 'STD',
            'itineraryFareMaskOption': 'N',
            'searchParams.departureDate': self.datetime_to_string(self.source_info.departure_date),
            'searchParams.returnDate': ''
        }


        status, text, headers = self.config.post_form('xbe/private/confirmationTab.action', data=data)




    def book(self, flight, fare, passengers, email, phone_number):
        self.source_info = fare.source.api_details

        selected_flight_list = [{"flightRPH": flight_ref.flight_rph, "departureTimeZulu": flight_ref.departure_time_zulu} for flight_ref in self.source_info.flight_refs]
        pax_details_adult = []
        pax_details_child = []
        pax_details_infant = []
        child_count = 0
        for passenger in passengers:
            passenger = passenger.passenger_model
            if passenger.age_group == PaxTypeChoices.ADULT or passenger.age_group == PaxTypeChoices.CHILD:
                data = {
                    "blacklisted": False,
                    "displayAdultAcco": None,
                    "displayAdultBal": None,
                    "displayAdultDOB": self.datetime_to_string(passenger.birth_date),
                    "displayAdultFirstName": passenger.first_name_english,
                    "displayAdultFirstNameOl": None,
                    "displayAdultLastName": passenger.last_name_english,
                    "displayAdultLastNameOl": None,
                    "displayAdultMCO": None,
                    "displayAdultNationality": "87",
                    "displayAdultPay": None,
                    "displayAdultSSRCode": "",
                    "displayAdultSSRInformation": "",
                    "displayAdultTitle": TitleTypeChoicesMap.to(passenger.title),
                    "displayAdultTitleOl": None,
                    "displayAdultType": "AD",
                    "displayETicketMask": None,
                    "displayInfantTravelling": "N",
                    "displayInfantWith": "",
                    "displayNameTranslationLanguage": None,
                    "displayNationalIDNo": "" if passenger.document_type == DocumentTypeChoices.PASSPORT else passenger.document_number,
                    "displayOrdePaxSequence": None,
                    "displayPaxCategory": "A",
                    "displayPaxSequence": None,
                    "displayPaxTravelReference": None,
                    "displayPnrPaxCatFOIDExpiry": self.datetime_to_string(passenger.document_expiry_date) if passenger.document_type == DocumentTypeChoices.PASSPORT else "",
                    "displayPnrPaxCatFOIDNumber": "" if passenger.document_type == DocumentTypeChoices.IRAN_ID else passenger.document_number,
                    "displayPnrPaxCatFOIDPlace":  passenger.document_issuance_county,
                    "displayPnrPaxCatFOIDType": None,
                    "displayPnrPaxPlaceOfBirth": "",
                    "displaySelectPax": None,
                    "displayTravelDocType": "",
                    "displayVisaApplicableCountry": "",
                    "displayVisaDocIssueDate": "",
                    "displayVisaDocNumber": "",
                    "displayVisaDocPlaceOfIssue": "",
                    "displaypnrPaxArrivalFlightNumber": None,
                    "displaypnrPaxArrivalTime": None,
                    "displaypnrPaxDepartureFlightNumber": None,
                    "displaypnrPaxDepartureTime": None,
                    "displaypnrPaxFltArrivalDate": None,
                    "displaypnrPaxFltDepartureDate": None,
                    "nameEditable": False,
                    "anci":[{}],
                    "removeAnci":[{}]
                }
                if passenger.age_group == PaxTypeChoices.ADULT:
                    data["displayAdultType"] = "AD"
                    pax_details_adult.append(data)
                elif passenger.age_group == PaxTypeChoices.CHILD:
                    data["displayAdultType"] = "CH"
                    pax_details_child.append(data)

            elif passenger.age_group == PaxTypeChoices.INFANT:
                child_count += 1
                data = {
                    "alertAutoCancellation": False,
                    "displayETicketMask": None,
                    "displayInfantAcco": None,
                    "displayInfantBal": None,
                    "displayInfantCharg": None,
                    "displayInfantDOB": self.datetime_to_string(passenger.birth_date),
                    "displayInfantFirstName": passenger.first_name_english,
                    "displayInfantFirstNameOl": None,
                    "displayInfantLastName": passenger.last_name_english,
                    "displayInfantLastNameOl": None,
                    "displayInfantMCO": None,
                    "displayInfantNationality": "87",
                    "displayInfantPay": None,
                    "displayInfantSSRCode": "",
                    "displayInfantSSRInformation": "",
                    "displayInfantSelect": None,
                    "displayInfantTitle": TitleTypeChoicesMap.to(passenger.title),
                    "displayInfantTitleOl": None,
                    "displayInfantTravellingWith": str(child_count),
                    "displayInfantType": "BABY",
                    "displayNameTranslationLanguage": None,
                    "displayNationalIDNo": "" if passenger.document_type == DocumentTypeChoices.PASSPORT else passenger.document_number,
                    "displayPaxCategory": "A",
                    "displayPaxSequence": None,
                    "displayPaxTravelReference": None,
                    "displayPnrPaxCatFOIDExpiry": self.datetime_to_string(passenger.document_expiry_date) if passenger.document_type == DocumentTypeChoices.PASSPORT else "",
                    "displayPnrPaxCatFOIDNumber": "" if passenger.document_type == DocumentTypeChoices.IRAN_ID else passenger.document_number,
                    "displayPnrPaxCatFOIDPlace": passenger.document_issuance_county,
                    "displayPnrPaxCatFOIDType": None,
                    "displayPnrPaxPlaceOfBirth": "",
                    "displayTravelDocType": "",
                    "displayVisaApplicableCountry": "",
                    "displayVisaDocIssueDate": "",
                    "displayVisaDocNumber": "",
                    "displayVisaDocPlaceOfIssue": "",
                    "displaypnrPaxArrivalFlightNumber": None,
                    "displaypnrPaxArrivalTime": None,
                    "displaypnrPaxDepartureFlightNumber": None,
                    "displaypnrPaxDepartureTime": None,
                    "displaypnrPaxFltArrivalDate": None,
                    "displaypnrPaxFltDepartureDate": None,
                    "nameEditable": False,
                    "sequenceNo": child_count
                }
                pax_details_infant.append(data)

        last_pax_id = 0
        for i, pax in enumerate(pax_details_adult):
            pax["seqNumber"] = i + 1
            pax["paxId"] = i
            if child_count > 0:
                pax["displayInfantWith"] = str(i + 1)
                pax["displayInfantTravelling"] = "Y"
            last_pax_id = i

        for i, pax in enumerate(pax_details_child, start=last_pax_id+1):
            pax["seqNumber"] = i + 1
            pax["paxId"] = i

        pax_details_adult_total = pax_details_adult + pax_details_child

        self.ancillary_block(pax_details_adult_total, selected_flight_list)
        self.confirmation_tab(pax_details_adult_total, pax_details_infant, selected_flight_list, email, phone_number)