from apps.core.exception import CoreException
import logging

class PartoException(CoreException):
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
    logger_message = "An exception occurred"
    # logger data
    logger_data = None



class PartoInvalidSessionException(PartoException):
    level = logging.ERROR
    # logger message
    logger_message = "Invalid Parto session"
    # logger data
    logger_data = None
    