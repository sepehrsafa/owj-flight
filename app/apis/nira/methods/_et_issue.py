import datetime
from apps.accounts.choices import PaxTypeChoices

from decimal import Decimal 
class ETIssue:
    method_name = 'ETIssueJS'

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


    def issue(self,pnr,email):
        data ={
            'AirLine':self.airline,
            'PNR':'pnr',
            'Email': email,
        }
         
        print(self.config.get(method=ETIssue.method_name, data=data))
        return

