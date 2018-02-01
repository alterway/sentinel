import docker
from adapters.orchestrators.orchestrator import OrchestratorAdapter
from models import Service, Node
from utils.dependencies_injection import inject_param


class SwarmAdapter(OrchestratorAdapter):

    def __init__(self):
        self.client = docker.DockerClient(base_url='unix://var/run/docker.sock', version='auto')

    def get_services(self):
        services = []
        if self._is_manager():
            swarm_services = self._get_swarm_services()

            for service in swarm_services:
                service_object = self._get_service_object(service)
                if service_object is not None:
                    services.append(service_object)

        return services

    def get_service(self, event):
        if event['Type'] == 'service' and self._is_manager():
            return self._get_service_object(self.client.services.get(event['Actor']['ID']))


    @inject_param('logger')
    def _get_service_object(self, service, logger=None):
        exposed_ports = self._get_service_exposed_ports(service)
        if len(exposed_ports) == 0:
            logger.info('Ignored Service : %s don\'t publish port' % service.attrs['Spec']['Name'])
        else:
            nodes = self._get_nodes_for_service(service)
            if len(nodes) == 0:
                logger.info('Ignored Service: %s don\'t run in available host' % service.attrs['Spec']['Name'])
            else:
                for port in exposed_ports:
                    return Service(name="%s-%s" % (service.attrs['Spec']['Name'], port), nodes=nodes, tags=['swarm-service'], port=port)

        return None

    def _is_manager(self):
        return self.client.info()['Swarm']['ControlAvailable']

    def _get_swarm_services(self):
        return self.client.services.list()

    def _get_nodes_for_service(self, swarm_service):
        result = []

        nodes = [node.attrs for node in self.client.nodes.list()]
        for node_attrs in nodes:
            if node_attrs['Status']['State'] == 'ready':
                result.append(Node(name=node_attrs['Description']['Hostname'], address=node_attrs['Status']['Addr']))

        return result

    def _get_service_exposed_ports(self, swarm_service):
        return [
            port['PublishedPort']
            for port in swarm_service.attrs['Spec']['EndpointSpec']['Ports']
        ] if 'Ports' in swarm_service.attrs['Spec']['EndpointSpec'] else []
