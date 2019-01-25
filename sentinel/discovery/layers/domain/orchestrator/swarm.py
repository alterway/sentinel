"""Implement adapter for Swarm orchestrator"""
import time
from typing import Union
from datetime import datetime
from datetime import timedelta
from zope.interface import implementer
from discovery.layers.domain.service.generalisation.interface.service import ServiceInterface
from discovery.layers.domain.service.generalisation.interface.swarm import SwarmInterface
from discovery.layers.domain.backend.generalisation.interface.backend import BackendInterface
from discovery.layers.domain.orchestrator.generalisation.interface.orchestrator import OrchestratorInterface
from ddd_domain_driven_design.domain.utils.multiton import Multiton


@implementer(OrchestratorInterface)
class Swarm(metaclass=Multiton):
    """ This class permit to get services in swarm cluster
    """

    suffix_method = ('create', 'start', 'update', 'remove', 'kill')

    def __init__(self,
                 backend: Union[BackendInterface, None],
                 service_swarm: Union[SwarmInterface, None],
                 service_container: Union[ServiceInterface, None],
                 logger=None
                 ):
        self.backend = backend
        self.service_swarm = service_swarm
        self.service_container = service_container
        self.logger = logger

    def get_services(self):
        """Get all running docker services, containers and swarmservices
        """
        services = []
        services.extend(self.service_swarm.get_services())
        services.extend(self.service_container.get_services())

        return services

    def get_service(self, event):
        """Get services from one docker service (container or swarm service)
        """
        # if we create a swarm service
        if event['Type'] == 'service':
            return self.service_swarm.get_services_from_id(event['Actor']['ID'])

        # if we create a container of a swarm service
        if (event['Type'] == 'container'
                and 'com.docker.swarm.service.id' in event['Actor']['Attributes']):
            return self.service_swarm.get_services_from_id(event['Actor']['Attributes']['com.docker.swarm.service.id'])

        # if we create a container of a no swarm service
        if event['Type'] == 'container':
            return self.service_container.get_services_from_id(event['Actor']['ID'])

        return []

    def listen_events(self, duration=None):
        """listen docker swarm events"""
        self.logger.info("Listen docker events...")
        client = self.service_swarm.get_client()
        until = None

        if duration is not None:
            until = datetime.now() + timedelta(seconds=duration)

        for event in client.events(since=datetime.utcnow(), until=until, decode=True):
            self._process_event(event)

    def _process_event(self, event):
        """Function to process docker event"""
        try:
            self.logger.info("Try with Event %s method to process", event['Action'])
            if event['Action'] in self.suffix_method:
                getattr(self, "_process_service_%s" % event['Action'])(event)
        except AttributeError:
            self.logger.info("Event %s has no method to process", event['Action'])

    def _process_service_start(self, event):
        self._process_service_create(event)

    def _process_service_create(self, event):
        self.logger.debug("Event create : %s" % event)
        services = self.get_service(event)
        for service in services:
            self.backend.register_service(service)

    def _process_service_update(self, event):
        self.logger.debug('Event Update : %s', event)
        if event['Type'] == 'node':
            attrs = event['Actor']['Attributes']
            if 'availability.new' in attrs:
                if attrs['availability.new'] == 'drain':
                    self._process_node_down(attrs['name'], 'drain')
                elif attrs['availability.new'] == 'active':
                    self._process_node_up(attrs['name'], 'active')
            elif 'state.new' in attrs:
                if attrs['state.new'] == 'down':
                    self._process_node_down(attrs['name'], 'down')
                elif attrs['state.new'] == 'ready':
                    self._process_node_up(attrs['name'], 'ready')
        elif event['Type'] == 'service':
            self._process_update_service(event)

    def _process_node_down(self, node_name, new_status):
        self.logger.info(
            'Swarm Node %s is %s, deregister this node in backend...',
            node_name, new_status
        )
        self.backend.deregister_node(node_name)

    def _process_node_up(self, node_name, new_status):
        self.logger.info(
            'Swarm Node %s is %s, process register services...',
            node_name, new_status
        )
        for service in self.get_services():
            service.nodes = [
                node
                for node in service.nodes
                if node.name == node_name
            ]
            self.backend.register_service(service)

    def _process_update_service(self, event):
        time.sleep(2)
        services = self.get_service(event)
        self._process_service_remove_or_kill(event)
        for service in services:
            self.backend.register_service(service)

    def _process_service_remove(self, event):
        self._process_service_remove_or_kill(event)

    def _process_service_kill(self, event):
        self._process_service_remove_or_kill(event)

    def _process_service_remove_or_kill(self, event):
        self.logger.debug("Get event remove : %s", event)

        # if we delete a container of a swarm service, we get all containers
        # with the same com.docker.swarm.service.id value
        services_containers_existed = None
        if (event['Type'] == 'container'
                and 'com.docker.swarm.service.id' in event['Actor']['Attributes']):
            time.sleep(5)
            services_containers_existed = self.service_swarm.get_containers_from_filters(
                {"label": "com.docker.swarm.service.id=%s" %
                    event['Actor']['Attributes']['com.docker.swarm.service.id']}
            )
            self.logger.debug(
                "%s containers of the %s service: %s",
                len(services_containers_existed),
                event['Actor']['Attributes']['com.docker.swarm.service.id'],
                event
            )

        event_tag_id = self.get_service_tag_to_id_remove(event)
        event_tag_name = self.get_service_tag_name_to_remove(event)

        service_node_id = None
        if 'com.docker.swarm.node.id' in event['Actor']['Attributes']:
            service_node_id = event['Actor']['Attributes']['com.docker.swarm.node.id']

        if (services_containers_existed is None and (event_tag_id is not None or event_tag_name is not None)) or (
                services_containers_existed is not None and len(services_containers_existed) == 0):
            self.backend.remove_service_with_tag(event_tag_id, event_tag_name, service_node_id)

    def get_service_tag_to_id_remove(self, event):
        """
        Get service tag ID from docker service type container or swarm service
        """
        # if we delete a swarm service
        if event['Type'] == 'service' and self.service_swarm.swarm_adapter.is_manager():
            return 'swarm-service:%s' % event['Actor']['ID']

        # if we delete a container of a swarm service
        if (event['Type'] == 'container'
                and 'com.docker.swarm.service.id' in event['Actor']['Attributes']):
            return 'swarm-service:%s' % event['Actor']['Attributes']['com.docker.swarm.service.id']

        # if we delete a container
        if (event['Type'] == 'container'
                and 'com.docker.swarm.service.name' not in event['Actor']['Attributes']):
            return 'container:%s' % event['Actor']['ID']

        self.logger.debug(
            "No tag id to remove %s type",
            event['Type']
        )

        return None

    def get_service_tag_name_to_remove(self, event):
        """
        Get service tag Attribut name from docker service type container or swarm service
        :param event:
        :return:
        """
        # if we delete a swarm service
        if event['Type'] == 'service' and self.service_swarm.swarm_adapter.is_manager():
            return 'service-name:%s' % event['Actor']['Attributes']['name']

        # if we delete a container of a swarm service
        if (event['Type'] == 'container'
                and 'com.docker.swarm.service.name' in event['Actor']['Attributes']):
            return 'service-name:%s' % event['Actor']['Attributes']['com.docker.swarm.service.name']

        # if we delete a container
        if (event['Type'] == 'container'
                and 'com.docker.swarm.service.name' not in event['Actor']['Attributes']):
            return 'service-name:%s' % event['Actor']['Attributes']['name']

        self.logger.debug(
            "No tag name to remove %s type",
            event['Type']
        )
