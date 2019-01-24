"""Set Service object from docker containers"""
import time
from typing import Union
from discovery.layers.domain.service.base import ServiceBase
from discovery.layers.domain.adapter.docker import DockerAdapter
from discovery.layers.domain.model.node import Node
from discovery.layers.domain.model.service import Service


class ContainerService(ServiceBase):
    """
    Adapter to manage docker container as service
    """

    def __init__(self, docker_adapter: Union[DockerAdapter, None], address=None, logger=None):
        ServiceBase.__init__(self, logger)

        self.address, self.port = address.split(':', 1)
        self.docker_adapter = docker_adapter

    def get_services_from_id(self, id):
        """
        Get services from container_id
        :param service_id:
        :return:
        """
        return self._get_services_object(id)

    def get_service_exposed_ports(self, id):
        """Get exposed ports from a swarm service ID"""
        container = self.docker_adapter.get_container_from_id(id)
        return self.docker_adapter.get_container_exposed_ports(container)

    def get_services(self):
        """
        Get services from running container
        :return:
        """
        services = []
        containers = [
            container
            for container in self.docker_adapter.list_container()
            if (
                    self.docker_adapter.container_is_running(container) and
                    self.docker_adapter.container_is_not_swarmservice(container)
            )
        ]

        for container in containers:
            services.extend(self._get_services_object(container.id))

        return services

    def _get_services_object(self, container_id):
        """
        :param container_id:
        :return: array
        """
        container = self.docker_adapter.get_container_from_id(container_id)
        waiting = 1
        # Wait if container is not running
        while not self.docker_adapter.container_is_running(container) and waiting < 10:
            self.logger.debug("container is not running, wait...")
            time.sleep(1)
            waiting += 1
            container = self.docker_adapter.get_container_from_id(container_id)

        exposed_ports = self.docker_adapter.get_container_exposed_ports(container)
        services = []
        if not exposed_ports and self.docker_adapter.container_is_not_swarmservice:
            self.logger.info(
                'Ignored Service : %s don\'t publish port',
                self.docker_adapter.get_container_name(container)
            )
        else:
            tags = ['container:%s' % container.id]
            labels, envs = self.docker_adapter.get_container_labels_and_vars(container)
            for port in exposed_ports:
                if self._has_to_be_registred(labels, envs, port['internal_port']):
                    tags.extend(self._get_tags(labels, envs, port['internal_port']))
                    name = self._get_name_from_label_and_envs(labels, envs, port['internal_port'])
                    services.append(
                        Service(
                            name=name if name is not None else "%s-%s" % (
                                self.docker_adapter.get_container_name(container),
                                port['internal_port']
                            ),
                            port=port['external_port'],
                            nodes=[
                                Node(
                                    nodeID=self.docker_adapter.get_local_node_id(),
                                    name=self.docker_adapter.get_local_node_name(),
                                    address=self.docker_adapter.get_local_node_address(self.address)
                                )
                            ],
                            tags=tags
                        )
                    )

        return services
