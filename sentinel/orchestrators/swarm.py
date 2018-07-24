from dependencies_injection.inject_param import inject_param
from zope.interface import implementer
from datetime import datetime
import time

from orchestrators.orchestrator import Orchestrator


@implementer(Orchestrator)
class Swarm(object):
    """ This class permit to get services in swarm cluster
    """
    @classmethod
    @inject_param("swarm_adapter")
    @inject_param("logger")
    def listen_events(cls, swarm_adapter=None, logger=None):
        logger.info("Listen docker events...")
        client = swarm_adapter.get_docker_socket()
        for event in client.events(since=datetime.utcnow(), decode=True):
            cls._process_event(event)

    @staticmethod
    @inject_param('container_adapter')
    @inject_param('swarmservice_adapter')
    def get_services(container_adapter=None, swarmservice_adapter=None):
        """Get all running docker services, containers and swarmservices
        """
        services = []
        services.extend(swarmservice_adapter.get_services())
        services.extend(container_adapter.get_services())
        return services

    @staticmethod
    @inject_param('swarmservice_adapter')
    @inject_param('container_adapter')
    def get_service(event, swarmservice_adapter=None, container_adapter=None):
        """Get services from one docker service (container or swarm service)
        """
        if event['Type'] == 'service':
            return swarmservice_adapter.get_services_from_id(event['Actor']['ID'])
        elif event['Type'] == 'container':
            return container_adapter.get_services_from_id(event['Actor']['ID'])

        return []

    @staticmethod
    @inject_param('swarm_adapter')
    @inject_param('logger')
    def get_service_tag_to_remove(event, swarm_adapter=None, logger=None):
        """Get service tag from docker service type container or swarm service
        """
        if event['Type'] == 'service' and swarm_adapter.is_manager():
            return 'swarm-service:%s' % event['Actor']['ID']
        elif event['Type'] == 'container' and 'com.docker.swarm.service.name' not in event['Actor']['Attributes']:
            return 'container:%s' % event['Actor']['ID']

        logger.debug("No tag to remove")
        return None

    @classmethod
    @inject_param('logger')
    def _process_event(cls, event, logger=None):
        """Function to process docker event"""
        try:
            getattr(cls, "_process_service_%s" % event['Action'])(event)
        except AttributeError:
            logger.info("Event %s has no method to process" % event['Action'])

    @classmethod
    @inject_param("backend_adapter")
    @inject_param("logger")
    def _process_service_create(cls, event, backend_adapter=None, logger=None):
        logger.debug("Get event create : %s" % event)
        services = cls.get_service(event)
        for service in services:
            backend_adapter.register_service(service)

    @classmethod
    @inject_param("logger")
    def _process_service_update(cls, event, logger=None):
        logger.debug('Event Update : %s' % event)
        if event['Type'] == 'node':
            attrs = event['Actor']['Attributes']
            if 'availability.new' in attrs:
                if attrs['availability.new'] == 'drain':
                    cls._process_node_down(attrs['name'], 'drain')
                elif attrs['availability.new'] == 'active':
                    cls._process_node_up(attrs['name'], 'active')
            elif 'state.new' in attrs:
                if attrs['state.new'] == 'down':
                    cls._process_node_down(attrs['name'], 'down')
                elif attrs['state.new'] == 'ready':
                    cls._process_node_up(attrs['name'], 'ready')
        elif event['Type'] == 'service':
            cls._process_update_service(event)

    @classmethod
    def _process_service_remove(cls, event):
        cls._process_service_remove_or_kill(event)

    @classmethod
    def _process_service_kill(cls, event):
        cls._process_service_remove_or_kill(event)

    @classmethod
    @inject_param("backend_adapter")
    @inject_param("logger")
    def _process_service_remove_or_kill(cls, event, backend_adapter=None, logger=None):
        logger.debug("Get event remove : %s" % event)
        tag_to_remove_on_backend = cls.get_service_tag_to_remove(event)
        if tag_to_remove_on_backend is not None:
            backend_adapter.remove_service_with_tag(tag_to_remove_on_backend)

    @staticmethod
    @inject_param('backend_adapter')
    @inject_param('logger')
    def _process_node_down(node_name, new_status, backend_adapter=None, logger=None):
        logger.info('Swarm Node %s is %s, deregister this node in backend...' % (node_name, new_status))
        backend_adapter.deregister_node(node_name)

    @classmethod
    @inject_param('backend_adapter')
    @inject_param('logger')
    def _process_node_up(cls, node_name, new_status, backend_adapter=None, logger=None):
        logger.info('Swarm Node %s is %s, process register services...' % (node_name, new_status))
        for service in cls.get_services():
            service.nodes = [
                node
                for node in service.nodes
                if node.name == node_name
            ]
            backend_adapter.register_service(service)

    @classmethod
    @inject_param('backend_adapter')
    def _process_update_service(cls, event, backend_adapter=None):
        time.sleep(2)
        services = cls.get_service(event)
        backend_adapter.remove_service_with_tag("swarm-service:%s" % event['Actor']['ID'])
        for service in services:
            backend_adapter.register_service(service)
