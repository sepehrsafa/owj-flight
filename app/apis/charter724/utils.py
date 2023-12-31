from app.enums import FareType, CabinType
import logging
def convert_fare_type(fare_type):
    if fare_type == "system":
        return FareType.PUBLIC
    elif fare_type == "charter":
        return FareType.CHARTER
    else:
        logging.warning(f"Unknown fare type: {fare_type} for charter724 api client")
        return FareType.UNKNOWN

def convert_cabin_type(cabin):
    cabin = cabin.lower()
    if cabin == "economy":
        return CabinType.ECONOMY
    elif cabin == "business":
        return CabinType.BUSINESS
    elif cabin == "first":
        return CabinType.FIRST
    else:
        logging.warning(f"Unknown cabin type: {cabin} for charter724 api client")
        return CabinType.UNKNOWN