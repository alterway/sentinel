from backends.backend import Backend
from models import Service, Node
from utils.dependencies_injection import inject_param
import os
import requests
import json
import time


class Consul(Backend):
    def __init__(self):
        self.address = os.environ.get(
            'CONSUL_ADDRESS'
        ) if os.environ.get('CONSUL_ADDRESS') is not None else "http://127.0.0.1:8500"

    @inject_param('docker_adapter')
    @inject_param('logger')
    def get_services(self, docker_adapter=None, logger=None):
        response = requests.get('%s/v1/catalog/services' % self.address).json()
        services = [
            Service(name=key, tags=response[key], nodes=[])
            for key in response.keys()
        ]
        local_services = []

        for service in sorted(services, key=lambda x: x.name):
            response = requests.get('%s/v1/catalog/service/%s' % (self.address, service.name)).json()
            for node in response:
                service.nodes.append(Node(address=node['Address'], name=node['Node']))
                service.port = node['ServicePort']

            logger.debug("Nodes for service %s are : %s" % (service.name, service.nodes))

        # Filter services not exist on local node
        local_node_name = docker_adapter.get_local_node_name()
        for service in services:
            for tag in service.tags:
                if "swarm-service" in tag:
                    local_services.append(service)
                    break
                elif "container" in tag and service.nodes[0].name == local_node_name:
                    local_services.append(service)
                    break

        return local_services

    @inject_param("logger")
    def register_service(self, service, logger=None):
        logger.debug("CONSUL - service to register: %s" % service.name)
        logger.debug("CONSUL - service to register for nodes : %s" % [node.address for node in service.nodes])
        for node in service.nodes:
            payload = {
                "ID": "%s-%s" % (service.name, node.name.split('.')[0]),
                "Name": service.name,
                "Tags": service.tags,
                "Address": str(node.address),
                "Port": service.port,
                "EnableTagOverride": True
            }

            logger.debug('Ask for register service %s : %s %s:%s' % (service.name, node.name, node.address, service.port))
            logger.debug('Payload : %s' % payload)

            attempt = 0
            passed = False
            while attempt < 10 and not passed:
                try:
                    response = requests.put(
                        'http://%s:8500/v1/agent/service/register' % node.address,
                        data=json.dumps(payload)
                    )
                    passed = True
                except requests.exceptions.ConnectionError:
                    logger.error("Can't connect to consul address: http://%s:8500" % node.address)
                    attempt += 1
                    time.sleep(1)  # Wait one second before retry

            if response and response.status_code == 200:
                logger.info("Register Service : %s - %s %s:%s" % (
                    service.name, node.name, node.address, service.port)
                )
            else:
                logger.error(
                    "Failed to register service %s for node %s : %s" % (
                        service.name, node.name, response.content
                    )
                )

    @inject_param("logger")
    def remove_service_with_tag(self, tag, logger=None):
        services = self.get_services()
        service_to_remove = [service for service in services if tag in service.tags]

        if len(service_to_remove) != 0:
            self.deregister_service(service_to_remove[0])
        else:
            logger.debug("Service with tag %s not found in consul" % tag)

    @inject_param('logger')
    def deregister_node(self, node_name, logger=None):
        payload = {
            'Node': node_name
        }
        response = requests.put('%s/v1/catalog/deregister' % self.address, data=json.dumps(payload))

        if response.status_code == 200 and response.json():
            logger.info('Deregister Node : %s ' % node_name)
        else:
            logger.error("Failed to deregister node %s : %s" % (node_name, response.content))

    @inject_param('logger')
    def deregister_service(self, service, logger=None):
        logger.debug("Process service %s to deregister on nodes : %s" % (service.name, service.nodes))

        for node in service.nodes:
            logger.debug("Process node %s to deregister service" % node.name)
            response = requests.put('http://%s:8500/v1/agent/service/deregister/%s' % (node.address, service.name))

            if response.status_code == 200:
                logger.info('Deregister Service : %s - %s' % (service.name, node.name))
            else:
                logger.error("Failed to deregister service %s for node %s : %s" % (service.name, node.name, response.content))
