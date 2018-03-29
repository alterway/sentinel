from utils.dependencies_injection import inject_param
from service.service_base import ServiceBase
from models import Service, Node
import time


class Container(ServiceBase):
    """ Adapter to manage docker container as service
    """
    @classmethod
    @inject_param('docker_adapter')
    def get_services(cls, docker_adapter=None):
        services = []
        containers = [
            container
            for container in docker_adapter.list_container()
            if docker_adapter.container_is_running(container) and docker_adapter.container_is_not_swarmservice(container)
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
        waiting = 1
        # Wait if container is not running
        while not docker_adapter.container_is_running(container) and waiting < 10:
            logger.debug("container is not running, wait...")
            time.sleep(1)
            waiting += 1
            container = docker_adapter.get_container_from_id(container_id)

        exposed_ports = docker_adapter.get_container_exposed_ports(container)
        services = []
        if len(exposed_ports) == 0:
            logger.info('Ignored Service : %s don\'t publish port' % docker_adapter.get_container_name(container))
        else:
            tags = ['container:%s' % container.id]
            labels, envs = docker_adapter.get_container_labels_and_vars(container)
            for port in exposed_ports:
                if cls._has_to_be_registred(labels, envs, port['internal_port']):
                    tags.extend(cls._get_tags(labels, envs, port['internal_port']))
                    name = cls._get_name_from_label_and_envs(labels, envs, port['internal_port'])
                    services.append(
                        Service(
                            name=name if name is not None else "%s-%s" % (
                                docker_adapter.get_container_name(container),
                                port['internal_port']
                            ),
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
