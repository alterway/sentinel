import docker
from orchestrator import OrechestratorAdapter
from sentinel.models import Service, Node

class SwarmAdapter():

    def __init__(self):
        self.client = docker.DockerClient(base_url='unix://var/run/docker.sock', version='auto')

    def get_services(self):
        services = []
        if self._is_manager():
            swarm_services = self._get_swarm_services()

            for service in swarm_services:
                exposed_ports = self._get_service_exposed_ports(service)
                if len(exposed_ports) == 0:
                    self.logger.info('Ignored Service : %s don\'t publish port')
                else:
                    nodes = self._get_nodes_for_service(service)
                    if len(nodes) == 0:
                        self.logger.info('Ignored Service: %s don\t run in available host')
                    else:
                        for port in exposed_ports:
                            services.append(Service(name="%s-%s" % (service.attrs['Spec']['Name'], port), nodes=nodes, tags=['swarm-service']))

        return services


    def _is_manager(self):
        return self.client.info()['Swarm']['ControlAvailable']

    def _get_swarm_services(self):
        return self.client.services.list()

    def _get_nodes_for_service(self, swarm_service):
        result = []

        nodes = [task['NodeID'] for task in service.get(service_id).tasks() if task['Status']['State'] == 'running']
        for node in nodes:
            node_attrs = self.client.nodes.get(node).attrs
            if node_attrs['Status']['State'] == 'ready':
                result.append(Node(name=node_attrs['Descrition']['Hostname'], address=node_attrs['Status']['Addr']))

        return result

    def _get_service_exposed_ports(self, swarm_service):
        return [
            port['PublishedPort']
            for port in service.attrs['Spec']['EndpointSpec']['Ports']
        ] if service.attrs['Spec']['EndpointSpec'].haskey('Ports') else []
