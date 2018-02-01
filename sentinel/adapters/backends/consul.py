import os
import requests
import json
from adapters.backends.backend import BackendAdapter
from models import Service, Node
from exceptions import RegisterFailed
from utils.dependencies_injection import inject_param


class ConsulAdapter(BackendAdapter):
    def __init__(self):
        self.address = os.environ.get('CONSUL_ADDRESS')

    def get_services(self):
        response = requests.get('%s/v1/catalog/services' % self.address).json()
        services = [
            Service(name=key, tags=response[key], port=0)
            for key in response.keys()
        ]

        for service in services:
            response = requests.get('%s/v1/catalog/service/%s' % (self.address, service.name)).json()
            for node in response:
                service.nodes.append(Node(address=node['Address'], name=node['Node']))
                service.port = node['ServicePort']

        return services

    @inject_param("logger")
    def register_service(self, service, logger=None):
        for node in service.nodes:
            payload = {
                'Node': node.name,
                'Address': node.address,
                'Service': {
                    'Service': service.name,
                    'Tags': service.tags,
                    'Address': node.address,
                    'Port': service.port
                }
            }

            response = requests.put('%s/v1/catalog/register' % self.address, data=json.dumps(payload))

            if response.json():
                logger.info("Register Service : %s - %s" % (service.name, node.name))
            else:
                logger.error("Failed to register service %s for node %s" % (service.name, node.name))








