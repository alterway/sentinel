"""Define consul adapter to use consul backend"""

import time
import requests
from zope.interface import implementer
from discovery.layers.domain.backend.generalisation.interface.backend import BackendInterface
from discovery.layers.domain.model.service import Service
from discovery.layers.domain.model.node import Node
from ddd_domain_driven_design.domain.utils.multiton import Multiton


@implementer(BackendInterface)
class Consul(metaclass=Multiton):
    """Consul adapter for consul backend"""

    def __init__(self, address=None, logger=None, adapter=None, ApiConsulFactory=None):
        address, port = address.split(':', 1)
        self.address = "%s:%s" % (address, port) if address is not None else "127.0.0.1:8500"
        self.port = port

        self.logger = logger
        self.adapter = adapter
        self.api_query = ApiConsulFactory.query()
        self.api_command = ApiConsulFactory.command()

    def get_services(self):
        """Get services register in consul"""
        local_services = []

        services = self.api_query.get_catalog_services(self.address)
        for service in sorted(services, key=lambda x: x.name):
            response = self.api_query.get_catalog_service(self.address, service.name)
            for consul_node in response:
                service.nodes.append(
                    Node(name=consul_node['Node'] if 'Node' in consul_node else None,
                         address=consul_node['Address'] if 'Address' in consul_node else None,
                         id=consul_node['ServiceID'] if 'ServiceID' in consul_node else None,
                         nodeID=consul_node['ServiceMeta']['NodeID'] if 'ServiceMeta' in consul_node and 'NodeID' in consul_node['ServiceMeta'] else None,
                         tags=consul_node['ServiceTags'] if 'ServiceTags' in consul_node else None
                         )
                )
                service.set_port(consul_node['ServicePort'])

            self.logger.debug(
                "Nodes for service %s are : %s",
                service.name, service.nodes
            )

        # Filter services witch not exist on local node
        local_node_name = self.adapter.get_local_node_name()
        for service in services:
            for tag in service.tags:
                if "swarm-service" in tag:
                    local_services.append(service)
                    break
                elif "container" in tag and service.nodes[0].name == local_node_name:
                    local_services.append(service)
                    break

        return local_services

    def register_service(self, service: Service):
        """Register a service in consul"""
        self.logger.debug(
            "CONSUL - Process to register service %s for nodes : %s",
            service.name,
            [node.address for node in service.nodes]
        )
        for node in service.nodes:
            payload = {
                "ID": "%s-%s-%s" % (service.name, node.name.split('.')[0], service.port),
                "Name": service.name,
                "Tags": service.tags,
                "Meta": {"NodeID": node.nodeID},
                "Address": str(node.address),
                "Port": service.port,
                "EnableTagOverride": True
            }
            backend_address = "%s:%s" % (node.address, self.port)

            self.logger.debug(
                "Process to register service %s on node %s with address %s and tags %s",
                service.name, node.name, backend_address, node.tags
            )
            self.logger.debug('Payload : %s', payload)

            attempt = 0
            passed = False
            while attempt < 10 and not passed:
                try:
                    response = self.api_command.register_service(backend_address, payload)
                    passed = True
                except requests.exceptions.ConnectionError:
                    self.logger.error(
                        "Can't connect to consul address: http://%s:%s",
                        node.address, self.port
                    )
                    attempt += 1
                    time.sleep(1)  # Wait one second before retry

            if response and response.status_code == 200:
                self.logger.info(
                    "Success to register service %s - %s to consul address: http://%s",
                    service.name, node.name, backend_address
                )
            else:
                self.logger.error(
                    "Failed to register service %s for node %s : %s",
                    service.name, node.name, response.content
                )

    def remove_service_with_tag(self, tag_id, tag_name=None, service_node_id=None):
        """Remove service which contains the given tag"""
        services = self.get_services()
        service_to_remove = [
            service
            for service in services
            if tag_id in service.tags or tag_name in service.tags
        ]

        if service_to_remove:
            self.logger.info("Try to deregister with tag_id %s, tag_name %s, nodeID %s in consul", tag_id, tag_name,
                             service_node_id)
            self.deregister_service(service_to_remove[0], tag_name, tag_id, service_node_id)
        else:
            self.logger.info("Service with tag_id %s, tag_name %s, nodeID %s not found in consul", tag_id, tag_name,
                             service_node_id)

    def deregister_service(self, service: Service, tag_name=None, tag_id=None, service_node_id=None):
        """Deregister a service in consul"""
        self.logger.debug(
            "CONSUL - Process to deregister service %s for nodes : %s",
            service.name,
            [node.address for node in service.nodes]
        )

        for node in service.nodes:
            backend_address = "%s:%s" % (node.address, self.port)
            self.logger.debug(
                "Process to deregister service %s on node %s (service_node: %s, nodeID: %s) with address %s and tag (id: %s, name %s) in tags %s",
                service.name, node.name, service_node_id, node.nodeID, backend_address, tag_id, tag_name, node.tags
            )

            if (tag_id is None and tag_name is None) or (tag_id in node.tags or tag_name in node.tags) and (
                    service_node_id is None or service_node_id == node.nodeID
            ):
                response = self.api_command.deregister_service(backend_address, node.id)
                if response.status_code == 200:
                    self.logger.info(
                        'Success to deregister service %s - %s - %s',
                        service.name, backend_address, node.id
                    )
                else:
                    self.logger.error(
                        "Failed to deregister service %s for node %s : %s",
                        service.name, node.name, response.content
                    )

    def deregister_node(self, node_name):
        """Deregister a node in consul"""
        payload = {
            'Node': node_name
        }
        response = self.api_command.deregister_node(self.address, payload)

        if response.status_code == 200 and response.json():
            self.logger.info('Success to deregister Node : %s ', node_name)
        else:
            self.logger.error(
                "Failed to deregister node %s : %s",
                node_name, response.content
            )
