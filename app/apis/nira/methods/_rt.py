import datetime
from apps.accounts.choices import PaxTypeChoices

from decimal import Decimal 
class RT:
    method_name = 'NRSRT.jsp'


    def __init__(self, client):
        self.client = client
        self.config = client.config
        self.airline = self.config.airline
        self.business_classes = self.config.business_classes

    @staticmethod
    def date_time_convertor(data):
        '''
        Convert date and time from string to datetime object
        '''
        return datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S').replace(tzinfo=None)

    def update_flight(self, flight, data):
        
        segment = flight.itineraries[0].segments[0]
        rt_segment = data['Segments'][0]
        segment.departure.iata_code = rt_segment['Origin']
        segment.departure.at = self.date_time_convertor(rt_segment['DepartureDT'])
        segment.arrival.iata_code = rt_segment['Destination']
        segment.flight_number = rt_segment['FlightNo']

    def _get_total_cost_for_pax(self, pax_type, rt_data):

        if pax_type == PaxTypeChoices.ADULT:
            return Decimal(rt_data['AdultTP'])
        elif pax_type == PaxTypeChoices.CHILD:
            return Decimal(rt_data['ChildTP'])
        elif pax_type == PaxTypeChoices.INFANT:
            return Decimal(rt_data['InfantTP'])

    def update_fare(self, fare, data):
        for pax in fare.per_pax_breakdown:
            pax.system_fare.total = self._get_total_cost_for_pax(pax.pax_type,data)


    def rt(self,pnr,complete):
        data ={
            'AirLine':self.airline,
            'PNR':pnr,
            'Complete': 'Y' if complete else 'N',
        }
        return self.config.get(method=RT.method_name, data=data)

