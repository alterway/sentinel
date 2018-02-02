import docker
from adapters.orchestrators.orchestrator import OrchestratorAdapter
from models import Service, Node
from utils.dependencies_injection import inject_param


class SwarmAdapter(OrchestratorAdapter):

    def __init__(self):
        self.client = docker.DockerClient(base_url='unix://var/run/docker.sock', version='auto')

    def get_services(self):
        services = []

        # If manager get swarm services
        if self._is_manager():
            swarm_services = self._get_swarm_services()

            for service in swarm_services:
                services.extend(self._get_services_object(service))

        # Get containers
        containers = self._get_containers()
        for container in containers:
            services.extend(self._get_services_object_from_container(container))

        return services

    def get_service(self, event):
        if event['Type'] == 'service' and self._is_manager():
            return self._get_services_object(self.client.services.get(event['Actor']['ID']))
        elif event['Type'] == 'container':
            return self._get_services_object_from_container(self.client.containers.get(event['Actor']['ID']))

        return []

    def get_service_tag_to_remove(self, event):
        if event['Type'] == 'service' and self._is_manager():
            return 'swarm-service:%s' % event['Actor']['ID']


    @inject_param('logger')
    def _get_services_object(self, service, logger=None):
        exposed_ports = self._get_service_exposed_ports(service)
        services = []
        if len(exposed_ports) == 0:
            logger.info('Ignored Service : %s don\'t publish port' % service.attrs['Spec']['Name'])
        else:
            nodes = self._get_nodes_for_service(service)
            if len(nodes) == 0:
                logger.info('Ignored Service: %s don\'t run in available host' % service.attrs['Spec']['Name'])
            else:
                for port in exposed_ports:
                    services.append(
                        Service(
                            name="%s-%s" % (service.attrs['Spec']['Name'], port),
                            nodes=nodes,
                            tags=['swarm-service:%s' % service.id],
                            port=port
                        )
                    )

        return services

    @inject_param('logger')
    def _get_services_object_from_container(self, container, logger=None):
        exposed_ports = self._get_container_exposed_ports(container)
        container_name = container.attrs['Config']['Labels']['com.docker.compose.service'] if 'com.docker.compose.service' in container.attrs['Config']['Labels'] else container.attrs['Name'].replace('/', '')
        services = []
        if len(exposed_ports) == 0:
            logger.info('Ignored Service : %s don\'t publish port' % container_name)
        else:
            for port in exposed_ports:
                services.append(
                    Service(
                        name="%s-%s" % (container_name, port),
                        port=port,
                        nodes=[
                            Node(
                                name=self.client.info()['Name'],
                                address=self.client.info()['Swarm']['NodeAddr']
                            )
                        ],
                        tags=['container:%s' % container.id]
                    )
                )

        return services

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


    def _get_containers(self):
        return [
            container
            for container in self.client.containers.list()
            if container.status == 'running' and 'com.docker.swarm.service.id' not in container.attrs['Config']['Labels']
        ]

    def _get_container_exposed_ports(self, container):
        ports = []
        for key in container.attrs['NetworkSettings']['Ports'].keys():
            if container.attrs['NetworkSettings']['Ports'][key] is not None and len(container.attrs['NetworkSettings']['Ports'][key][0]['HostPort']) != 0:
                ports.append(int(container.attrs['NetworkSettings']['Ports'][key][0]['HostPort']))

        return ports
