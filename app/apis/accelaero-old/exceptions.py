from apps.core.exception import CoreException
import logging

class AccelAeroException(CoreException):
    # API html response code
    status_code = 500
    # API response error detail text
    response_detail = 'A server error occurred.'
    # API response error detail code
    response_code = 'error'
    # API response system code corresponding to detail and logger
    system_code = 500

    # logging data
    level = logging.INFO
    logger = logging.getLogger(__name__)

    # logger message
    logger_message = "An exception occurred in AccelAero"
    # logger data
    logger_data = None