import requests
import json
from ddd_domain_driven_design.domain.utils.multiton import Multiton


class Command(metaclass=Multiton):
    """
    Adapter to request Query Consul API
    """

    @staticmethod
    def register_service(node_address, payload):
        return requests.put(
            'http://%s/v1/agent/service/register' % node_address,
            data=json.dumps(payload),
            timeout=1
        )

    @staticmethod
    def deregister_service(node_address, service_id):
        return requests.put(
            'http://%s/v1/agent/service/deregister/%s' % (
                node_address, service_id
            ),
            timeout=1
        )

    @staticmethod
    def deregister_node(node_address, payload):
        return requests.put(
            'http://%s/v1/catalog/deregister' % node_address,
            data=json.dumps(payload),
            timeout=1
        )
