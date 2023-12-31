from apps.flights.services.apis.base.config import BaseConfig
from .exceptions import NiraException
import logging
import requests
from django.core.cache import cache as django_cache
import json
import hashlib



class Config(BaseConfig):

    _system_code = 1
    _session = requests.Session()


    def __init__(self, username, password, agency_api_id,search_result_cache_lifespan,filter,extra_data, timeout=None, max_retries=None, backoff_factor=None, retry_statuses=None, retry_methods=None, additional_headers=None):

        super().__init__(username, password, agency_api_id,search_result_cache_lifespan,filter, timeout, max_retries,
                         backoff_factor, retry_statuses, retry_methods, additional_headers)
        self.airline = extra_data.get('airline')
        self.default_luggage = extra_data.get('default_luggage')
        self.business_classes = extra_data.get('business_classes')
        self.base_url = extra_data.get('base_urls')
        self.fare_info_cache_time = extra_data.get('fare_info_cache_time',0)
        self.restricted_classes = extra_data.get('restricted_classes',[])
        self.for_which_nationalities_is_sale_restricted = extra_data.get('for_which_nationalities_is_sale_restricted',[])

    def prepare_data(self, data):
        data['OfficeUser'] = self.username
        data['OfficePass'] = self.password
        return data

    def handel_response(self, res):
        if res.status_code != 200:
            logging.error(f'Nira Status Code = {res.status_code}',res.text)

            raise NiraException(f'Nira Status Code = {res.status_code}', res.text)

        res_data = res.text.replace('\r\n', '\\n')
        try:
            res_data = json.loads(res_data)

        except Exception as e:
            logging.error(e)
            raise NiraException(f'Nira Unable to parse JSON.', data=res.text)

        return res_data

    def get(self, method, data=None):

        url = self.base_url[method]+'/'+method
        data = self.prepare_data(data) 
        res = self._session.get(
                url,
                params=data,
                timeout=self.timeout,
                #adapter=self.adapter,
            )
        return self.handel_response(res)


    def post(self, method, data):

        url = self.base_url[method]+'/'+method
        data = self.prepare_data(data)
        res = self._session.post(
                url,
                data=data,
                timeout=self.timeout,
                #adapter=self.adapter,
            )

        return self.handel_response(res)