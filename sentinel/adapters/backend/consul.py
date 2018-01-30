import os
import requests
import json
from backend import BackendAdapter
from sentinel.models import Service, Node
from sentinel.exceptions import RegisterFailed


class Consul(BackendAdapter):
    def __init__(self):
        self.address = os.environ.get('CONSUL_ADDRESS')

    def get_services(self):
        response = requests.get('%s/v1/catalog/services' % self.address).json()
        services = [
            Service(name=key, tags=response[key])
            for key in response.keys()
        ]

        for service in services:
            response = requests.get('%s/v1/catalog/service/%s' % (self.address, service.name)).json()
            for node in response:
                service.nodes.append(Node(address=response['Address'], name=response['Node']))
                service.port = node['ServicePort']

        return services

    def register_service(self, service):
        for node in service.nodes:
            payload = {
                'Node': node.name,
                'Address': node.Address,
                'Service': {
                    'Service': service.name,
                    'Tags': service.tags,
                    'Address': node.address,
                    'Port': service.port
                }
            }

            response = requests.put('%s/v1/catalog/register' % self.address, data=json.dumps(payload))

            if not response.json():
                raise RegisterFailed("Register service %s in consul failed for node %s" % (service.name, node.name))








