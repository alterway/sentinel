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

    @inject_param('logger')
    def get_services(self, logger=None):
        response = requests.get('%s/v1/catalog/services' % self.address).json()
        services = [
            Service(name=key, tags=response[key], port=0, nodes=[])
            for key in response.keys()
        ]

        for service in services:
            response = requests.get('%s/v1/catalog/service/%s' % (self.address, service.name)).json()
            for node in response:
                service.nodes.append(Node(address=node['Address'], name=node['Node']))
                service.port = node['ServicePort']

            logger.debug("Nodes for service %s are : %s" % (service.name, service.nodes))

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

    @inject_param("logger")
    def remove_service_with_tag(self, tag, logger=None):
        services = self.get_services()
        for service in services:
            if tag in service.tags:
                logger.debug("Process service %s to deregister on nodes : %s" % (service.name, service.nodes))
                for node in service.nodes:
                    logger.debug("Process node %s to deregister service" % node.name)
                    payload = {
                        'Node': node.name,
                        'ServiceID': service.name
                    }

                    response = requests.put('%s/v1/catalog/deregister' % self.address, data=json.dumps(payload))

                    if response.status_code == 200 and response.json():
                        logger.info('Deregister Service : %s - %s' % (service.name, node.name))
                    else:
                        logger.error("Failed to deregister service %s for node %s : %s" % (service.name, node.name, response.content))








