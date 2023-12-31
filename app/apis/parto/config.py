from apps.flights.services.apis.base.config import BaseConfig
from .exceptions import PartoInvalidSessionException
import logging
import requests
from django.core.cache import cache as django_cache
import json
import hashlib

class Config(BaseConfig):

    _system_code = 3
    session = requests.Session()
    
    def __init__(self, username, password,agency_api_id,search_result_cache_lifespan, filter,extra_data, timeout=None, max_retries=None, backoff_factor=None, retry_statuses=None, retry_methods=None, additional_headers=None):

        super().__init__(username, password,agency_api_id,search_result_cache_lifespan, filter, timeout, max_retries,
                         backoff_factor, retry_statuses, retry_methods, additional_headers)
        self.url = extra_data.get('url')
        self.session_cache_lifespan = extra_data.get('session_cache_lifespan',5000)
        self.session_id = None


    def get():
        pass

    def post(self, method, data=None, add_session_id=True):

        if add_session_id:
            data['SessionId'] = self.session_id

        res = self.session.post(
                self.url+"/"+method,
                json=data,
                timeout=self.timeout,
            ).json()

        if(res['Error']):
            if(res['Error']['Id'] == 'Err0102008'):
                raise PartoInvalidSessionException()

        return res

