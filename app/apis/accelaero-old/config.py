from apps.flights.services.apis.base.config import BaseConfig
from .exceptions import AccelAeroException
import logging
import requests
from django.core.cache import cache as django_cache
import json
import hashlib

class Config(BaseConfig):

    _system_code = 2
    


    def __init__(self, username, password,agency_api_id,search_result_cache_lifespan, filter,extra_data, timeout=None, max_retries=None, backoff_factor=None, retry_statuses=None, retry_methods=None, additional_headers=None):

        super().__init__(username, password,agency_api_id,search_result_cache_lifespan, filter, timeout, max_retries,
                         backoff_factor, retry_statuses, retry_methods, additional_headers)
        self.airline = extra_data.get('airline')
        self.webservice_url = extra_data.get('url')+'/webservices/services/AAResWebServices'
        self.site_url = extra_data.get('url')
        self.booking_chanel = extra_data.get('booking_chanel')
        self.terminal_id = extra_data.get('terminal_id')
        self.requestor_id_type = extra_data.get('requestor_id_type')
        self.base_header = {
            'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US, en; q=0.7, fa; q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Host': 'reservations.mahan.aero',
            'Origin': 'http://reservations.mahan.aero',
        }
        self.session = requests.Session()
        self.session.headers.update(self.base_header)

    def get_hash(self,method,data):
        return hashlib.md5(f'{self.airline}-{method}-{data}'.encode("utf-8")).hexdigest()
        return (f'{self.airline}-{method}-{data}')

    def get(self, method, headers={}):

        response = self.session.get(f'{self.site_url}/{method}')

        return response.status_code, response.text, response.headers


    def post_form(self, method, data, headers={}):

        response = self.session.post(f'{self.site_url}/{method}', data=data, headers=headers)

        return response.status_code, response.text, response.headers



    def post(self, data):

        final_data = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.opentravel.org/OTA/2003/05">
                <soapenv:Header>
                    <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
                        <wsse:UsernameToken>
                            <wsse:Username>{self.username}</wsse:Username>
                            <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{self.password}</wsse:Password>
                        </wsse:UsernameToken>
                    </wsse:Security>
                </soapenv:Header>
                <soapenv:Body>
                {data}
                </soapenv:Body>
            </soapenv:Envelope>
        """
        final_header={'content-type': 'text/xml'}
        res = self.session.post(
                self.webservice_url,
                headers=final_header,
                data=final_data,
                timeout=self.timeout,
            )

        '''
        if res.status_code != 200:
            raise AccelAeroException(message=f'AccelAero Status Code = {res.status_code}', data=res.text)
        '''


        return {"data":res.content,"headers":res.headers}
