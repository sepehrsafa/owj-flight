import logging

from django.core.cache import cache as django_cache

logger = logging.getLogger(__name__)


class Fare:

    method_name = 'FareJS.jsp'

    def __init__(self, client):
        self.client = client
        self.config = client.config
        self.airline = self.config.airline
        self.cache_time = self.config.fare_info_cache_time

    def get_rule(self, origin, destination, flight_class, cache=True):

        key = f'api:flight:nira:fare:{self.airline}:{origin}:{destination}:{flight_class}'

        if cache:
            logger.debug(f'Nira Fare Rule Cache Hit: {key}')
            rule = django_cache.get(key)
            if rule:
                logger.debug(f'Fare available in cache: {key}')
                return rule

        params = {
            'Route': origin+'-'+destination,
            'RBD': flight_class,
        }

        logger.debug(f'Fetching Fare Rule from Nira: {key}')
        fare = self.config.get(method=self.method_name, data=params)

        fare['flight_class'] = flight_class
        logger.debug(f'setting Fare Rule in cache: {key} with timeout {self.cache_time}')
        django_cache.set(key, fare, timeout=self.cache_time)

        return fare