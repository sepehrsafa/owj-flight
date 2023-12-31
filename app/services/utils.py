from app.models import APIs
from app.enums import APIClient
from app.apis import Charter724Client, AccelAeroClient
from owjcommon.logger import TraceLogger


clients_instances = {}
api_clients = {
    APIClient.CHARTER724: Charter724Client,
    APIClient.ACCELAERO: AccelAeroClient,
}
logger = TraceLogger(__name__)


def get_api_client(api: APIs, trace_id: str = None):
    if api.id not in clients_instances:
        logger.info(
            f"Creating client for api {api.id} with client {api.client}", trace_id
        )
        
        clients_instances[api.id] = api_clients[api.client](
            id=api.id,
            url=api.url,
            key=api.key,
            secret=api.secret,
            extra=api.extra,
            search_timeout=api.search_timeout,
        )
        
    client = clients_instances[api.id]
    return client
