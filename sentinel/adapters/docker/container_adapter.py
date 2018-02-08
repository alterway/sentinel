from utils.dependencies_injection import inject_param
from adapters.docker.service_adapter import ServiceAdapter
from models import Service, Node
import time


class ContainerAdapter(ServiceAdapter):

    @inject_param('docker_adapter')
    def get_services(self, docker_adapter=None):
        services = []
        containers = [
            container
            for container in docker_adapter.list_container()
            if container.status == 'running' and 'com.docker.swarm.service.id' not in container.attrs['Config']['Labels']
        ]

        for container in containers:
            services.extend(self._get_services_object(container.id))

        return services

    def get_services_from_id(self, container_id):
        return self._get_services_object(container_id)

    @inject_param('docker_adapter')
    @inject_param('logger')
    def _get_services_object(self, container_id, docker_adapter=None, logger=None):
        container = docker_adapter.get_container_from_id(container_id)
        waiting = 0
        # Wait if container is not running
        while container.attrs['State']['Status'] != "running" and waiting != 10:
            logger.debug("container status : %s wait..." % container.attrs['State']['Status'])
            time.sleep(1)
            waiting += 1
            container = docker_adapter.get_container_from_id(container_id)

        exposed_ports = self._get_container_exposed_ports(container)
        container_name = container.attrs['Config']['Labels']['com.docker.compose.service'] if 'com.docker.compose.service' in container.attrs['Config']['Labels'] else container.attrs['Name'].replace('/', '')
        services = []
        if len(exposed_ports) == 0:
            logger.info('Ignored Service : %s don\'t publish port' % container_name)
        else:
            for port in exposed_ports:
                tags = ['container:%s' % container.id]
                labels, envs = self._get_container_labels_and_vars(container)
                tags.extend(self._get_tags(labels, envs, port['internal_port']))
                name = self._get_name_from_label_and_envs(labels, envs, port['internal_port'])
                services.append(
                    Service(
                        name=name if name is not None else "%s-%s" % (container_name, port['internal_port']),
                        port=port['external_port'],
                        nodes=[
                            Node(
                                name=docker_adapter.get_local_node_name(),
                                address=docker_adapter.get_local_node_address()
                            )
                        ],
                        tags=tags
                    )
                )

        return services

    @inject_param('logger')
    def _get_container_exposed_ports(self, container, logger=None):
        ports = []
        logger.debug("NetworkSetting : %s" % container.attrs['NetworkSettings']['Ports'])
        for key in container.attrs['NetworkSettings']['Ports'].keys():
            if container.attrs['NetworkSettings']['Ports'][key] is not None and len(container.attrs['NetworkSettings']['Ports'][key][0]['HostPort']) != 0:
                ports.append({
                    'internal_port': int(key.replace('/tcp', '').replace('/udp', '')),
                    'external_port': int(container.attrs['NetworkSettings']['Ports'][key][0]['HostPort'])
                })

        logger.debug('ports : %s' % ports)
        return ports

    @inject_param('logger')
    def _get_container_labels_and_vars(self, container, logger=None):
        labels = container.attrs['Config']['Labels']
        logger.debug("labels : %s" % labels)
        envs = [
            env
            for env in container.attrs['Config']['Env']
        ] if 'Env' in container.attrs['Config'] else []

        return labels, envs
