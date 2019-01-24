"""Set Service object from swarm services"""
from typing import Union
from discovery.layers.domain.service.base import ServiceBase
from discovery.layers.domain.adapter.swarm import SwarmAdapter
from discovery.layers.domain.model.node import Node
from discovery.layers.domain.model.service import Service
from discovery.layers.infrastructure.exceptions import InvalidIPAddress


class SwarmService(ServiceBase):
    """ Adaper to manage docker swarm service as sentinel Services objects
    """

    def __init__(self, swarm_adapter: Union[SwarmAdapter, None], logger=None):
        ServiceBase.__init__(self, logger)

        self.swarm_adapter = swarm_adapter

    def get_client(self):
        return self.swarm_adapter.get_docker_socket()

    def get_containers_from_filters(self, filters: dict) -> Union[list, None]:
        """Get all containers of a service from filters"""
        return self.swarm_adapter.get_containers_from_filters(filters=filters)

    def get_services_from_id(self, id):
        """Get services from a swarm service ID"""

        if self.swarm_adapter.is_manager():
            return self._get_services_object(
                self.swarm_adapter.get_swarm_service_by_id(id)
            )

        return []

    def get_services_from_filters(self, filters: dict) -> Union[list, None]:
        return self.swarm_adapter.get_swarm_services_from_filters(filters=filters)

    def get_service_exposed_ports(self, id):
        """Get exposed ports from a swarm service ID"""
        service = self.swarm_adapter.get_swarm_service_by_id(id)
        return self.swarm_adapter.get_swarmservice_exposed_ports(service)

    def get_services(self):
        """Get services from running swarm services"""
        services = []
        
        # If manager get swarm services
        if self.swarm_adapter.is_manager():
            swarm_services = self.swarm_adapter.get_swarm_services()

            for service in swarm_services:
                services.extend(self._get_services_object(service))

        return services

    def _get_services_object(self, service):
        service_name = self.swarm_adapter.get_swarmservice_name(service)
        exposed_ports = self.swarm_adapter.get_swarmservice_exposed_ports(service)
        service_networks = self.swarm_adapter.get_swarmservice_networks(swarmservice=service)
        service_running_containers = self.get_containers_from_filters(
                {"label": "com.docker.swarm.service.id=%s" % service.id}
            )
        services = []
        tags = []

        if not exposed_ports:
            self.logger.info('Ignored Service : %s does not publish port', service_name)
        else:
            all_nodes = self._get_all_nodes()
            running_nodes = self._get_nodes_running_service(service)
            if not all_nodes and not running_nodes:
                self.logger.info('Ignored Service: %s don\'t run in available host', service_name)
            else:
                tags.append('swarm-service:%s' % service.id)
                tags.append('service-name:%s' % service_name)
                for network in service_networks:
                    tags.append('service-network:%s' % network.name)

                labels, envs = self.swarm_adapter.get_swarmservice_labels_and_vars(service)
                for port in exposed_ports:
                    if self._has_to_be_registred(labels, envs, port['internal_port']):
                        tags.extend(self._get_tags(labels, envs, port['internal_port']))
                        name = self._get_name_from_label_and_envs(
                            labels, envs, port['internal_port']
                        )
                        services.append(
                            Service(
                                name=name if name is not None else "%s-%s" % (service_name, port['external_port']),
                                # nodes=all_nodes if port['mode'] == 'ingress' else running_nodes,
                                nodes=running_nodes,
                                running_containers=service_running_containers,
                                tags=tags,
                                port=port['external_port']
                            )
                        )

            for srv in services:
                self.logger.debug(": %s", srv.__dict__)

        return services

    def get_swarm_node_from_id(self, id):
        """
        Get services from container_id
        :param service_id:
        :return:
        """
        return self.docker_adapter.get_swarm_node_from_id(id)

    def _get_all_nodes(self):
        all_nodes = []

        for node in self.swarm_adapter.list_nodes():
            if self.swarm_adapter.is_ready(node):
                all_nodes = self._add_node_to_list(all_nodes, node)

        return all_nodes

    def _get_nodes_running_service(self, swarm_service):
        running_nodes_ids = [
            task['NodeID']
            for task in self.swarm_adapter.get_swarm_service_tasks(swarm_service)
            if 'NodeID' in task
        ]
        self.logger.debug(
            'SwarmService %s - Nodes ID running service are %s',
            swarm_service.name, running_nodes_ids
        )
        all_nodes = self.swarm_adapter.list_nodes()
        running_nodes = []
        for node in all_nodes:
            if node.attrs['ID'] in running_nodes_ids and self.swarm_adapter.is_ready(node):
                running_nodes = self._add_node_to_list(running_nodes, node)

        self.logger.debug('SwarmService %s - Nodes running service are %s', swarm_service.name, [
            node.name for node in running_nodes
        ])
        return running_nodes

    def _add_node_to_list(self, node_list, swarmnode_to_add):
        try:
            node_list.append(
                Node(
                    nodeID=self.swarm_adapter.get_swarmnode_id(swarmnode_to_add),
                    name=self.swarm_adapter.get_swarmnode_name(swarmnode_to_add),
                    address=self.swarm_adapter.get_swarmnode_address(swarmnode_to_add)
                )
            )
        except InvalidIPAddress as error:
            self.logger.warning(
                "Can't add node %s : %s",
                self.swarm_adapter.get_swarmnode_name(swarmnode_to_add),
                error.message
            )

        return node_list
