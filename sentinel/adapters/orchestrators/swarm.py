from adapters.orchestrators.orchestrator import OrchestratorAdapter
from utils.dependencies_injection import inject_param
import time


class SwarmAdapter(OrchestratorAdapter):
    """ This class permit to get services in swarm cluster
    """

    @classmethod
    @inject_param('logger')
    def process_event(self, event, logger=None):
        """Function for specials docker event treatments
        """
        if event['Action'] == 'update':
            logger.debug('Event Update : %s' % event)
            if event['Type'] == 'node':
                attrs = event['Actor']['Attributes']
                if 'availability.new' in attrs:
                    if attrs['availability.new'] == 'drain':
                        SwarmAdapter._process_node_down(attrs['name'], 'drain')
                    elif attrs['availability.new'] == 'active':
                        self._process_node_up(attrs['name'], 'active')
                elif 'state.new' in attrs:
                    if attrs['state.new'] == 'down':
                        SwarmAdapter._process_node_down(attrs['name'], 'down')
                    elif attrs['state.new'] == 'ready':
                        self._process_node_up(attrs['name'], 'ready')
            elif event['Type'] == 'service':
                SwarmAdapter._process_update_service(event)

    @staticmethod
    @inject_param('backend_adapter')
    @inject_param('logger')
    def _process_node_down(node_name, new_status, backend_adapter=None, logger=None):
        logger.info('Swarm Node %s is %s, deregister this node in backend...' % (node_name, new_status))
        backend_adapter.deregister_node(node_name)

    @inject_param('backend_adapter')
    @inject_param('logger')
    def _process_node_up(self, node_name, new_status, backend_adapter=None, logger=None):
        logger.info('Swarm Node %s is %s, process register services...' % (node_name, new_status))
        for service in self.get_services():
            backend_adapter.register_service(service)

    @classmethod
    @inject_param('backend_adapter')
    def _process_update_service(self, event, backend_adapter=None):
        time.sleep(2)
        services = self.get_service(event)
        backend_adapter.remove_service_with_tag("swarm-service:%s" % event['Actor']['ID'])
        for service in services:
            backend_adapter.register_service(service)

    @classmethod
    @inject_param('container_adapter')
    @inject_param('swarmservice_adapter')
    def get_services(self, container_adapter=None, swarmservice_adapter=None):
        """Get all running docker services, containers and swarmservices
        """
        services = []
        services.extend(swarmservice_adapter.get_services())
        services.extend(container_adapter.get_services())
        return services

    @classmethod
    @inject_param('swarmservice_adapter')
    @inject_param('container_adapter')
    def get_service(self, event, docker_adapter=None, swarmservice_adapter=None, container_adapter=None):
        """Get services from one docker service (container or swarm service)
        """
        if event['Type'] == 'service':
            return swarmservice_adapter.get_services_from_id(event['Actor']['ID'])
        elif event['Type'] == 'container':
            return container_adapter.get_services_from_id(event['Actor']['ID'])

        return []

    @classmethod
    @inject_param('docker_adapter')
    @inject_param('logger')
    def get_service_tag_to_remove(self, event, docker_adapter=None, logger=None):
        """Get service tag from docker service type container or swarm service
        """
        if event['Type'] == 'service' and docker_adapter.is_manager():
            return 'swarm-service:%s' % event['Actor']['ID']
        elif event['Type'] == 'container' and 'com.docker.swarm.service.name' not in event['Actor']['Attributes']:
            return 'container:%s' % event['Actor']['ID']
        else:
            logger.debug("No tag to remove")
            return None
