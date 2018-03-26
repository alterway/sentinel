from utils.dependencies_injection import inject_param
from services_adapters.service_adapter import ServiceAdapter
from models import Service, Node
import time


class Container(ServiceAdapter):
    """ Adapter to manage docker container as service
    """
    @classmethod
    @inject_param('docker_adapter')
    def get_services(cls, docker_adapter=None):
        services = []
        containers = [
            container
            for container in docker_adapter.list_container()
            if container.status == 'running' and 'com.docker.swarm.service.id' not in container.attrs['Config']['Labels']
        ]

        for container in containers:
            services.extend(cls._get_services_object(container.id))

        return services

    @classmethod
    def get_services_from_id(cls, container_id):
        return cls._get_services_object(container_id)

    @classmethod
    @inject_param('docker_adapter')
    @inject_param('logger')
    def _get_services_object(cls, container_id, docker_adapter=None, logger=None):
        container = docker_adapter.get_container_from_id(container_id)
        waiting = 0
        # Wait if container is not running
        while container.attrs['State']['Status'] != "running" and waiting != 10:
            logger.debug("container status : %s wait..." % container.attrs['State']['Status'])
            time.sleep(1)
            waiting += 1
            container = docker_adapter.get_container_from_id(container_id)

        exposed_ports = cls._get_container_exposed_ports(container)
        container_name = container.attrs['Config']['Labels']['com.docker.compose.service'] if 'com.docker.compose.service' in container.attrs['Config']['Labels'] else container.attrs['Name'].replace('/', '')
        services = []
        if len(exposed_ports) == 0:
            logger.info('Ignored Service : %s don\'t publish port' % container_name)
        else:
            tags = ['container:%s' % container.id]
            labels, envs = cls._get_container_labels_and_vars(container)
            for port in exposed_ports:
                if cls._has_to_be_registred(labels, envs, port['internal_port']):
                    tags.extend(cls._get_tags(labels, envs, port['internal_port']))
                    name = cls._get_name_from_label_and_envs(labels, envs, port['internal_port'])
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

    @staticmethod
    @inject_param('logger')
    def _get_container_exposed_ports(container, logger=None):
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

    @staticmethod
    @inject_param('logger')
    def _get_container_labels_and_vars(container, logger=None):
        labels = container.attrs['Config']['Labels']
        logger.debug("labels : %s" % labels)
        envs = [
            env
            for env in container.attrs['Config']['Env']
        ] if 'Env' in container.attrs['Config'] else []

        return labels, envs
