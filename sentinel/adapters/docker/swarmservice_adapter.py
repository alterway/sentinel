from adapters.docker.service_adapter import ServiceAdapter

from models import Node, Service

from utils.dependencies_injection import inject_param


class SwarmServiceAdapter(ServiceAdapter):
    """ Adaper to manage docker swarm service as service
    """

    @inject_param('docker_adapter')
    def get_services(self, docker_adapter=None):
        services = []

        # If manager get swarm services
        if docker_adapter.is_manager():
            swarm_services = docker_adapter.get_swarm_services()

            for service in swarm_services:
                services.extend(self._get_services_object(service))

        return services

    @inject_param('docker_adapter')
    def get_services_from_id(self, service_id, docker_adapter=None):
        if docker_adapter.is_manager():
            return self._get_services_object(docker_adapter.get_swarm_service_by_id(service_id))
        else:
            return []

    @inject_param('logger')
    def _get_services_object(self, service, logger=None):
        exposed_ports = self._get_service_exposed_ports(service)
        services = []
        if len(exposed_ports) == 0:
            logger.info('Ignored Service : %s don\'t publish port' % service.attrs['Spec']['Name'])
        else:
            all_nodes = self._get_nodes_for_service(service)
            running_nodes = self._get_nodes_running_service(service)
            if len(all_nodes) == 0 and len(running_nodes) == 0:
                logger.info('Ignored Service: %s don\'t run in available host' % service.attrs['Spec']['Name'])
            else:
                tags = ['swarm-service:%s' % service.id]
                labels, envs = self._get_swarm_service_labels_and_vars(service)
                for port in exposed_ports:
                    if self._has_to_be_registred(labels, envs, port['internal_port']):
                        tags.extend(self._get_tags(labels, envs, port['internal_port']))
                        name = self._get_name_from_label_and_envs(labels, envs, port['internal_port'])
                        services.append(
                            Service(
                                name=name if name is not None else "%s-%s" % (service.attrs['Spec']['Name'], port['external_port']),
                                nodes=all_nodes if port['mode'] == 'ingress' else running_nodes,
                                tags=tags,
                                port=port['external_port']
                            )
                        )

            for service in services:
                logger.debug(": %s" % service.__dict__)

        return services

    @inject_param('docker_adapter')
    def _get_nodes_for_service(self, swarm_service, docker_adapter=None):
        result = []

        nodes = [node.attrs for node in docker_adapter.list_nodes()]
        for node_attrs in nodes:
            if node_attrs['Status']['State'] == 'ready':
                result.append(Node(name=node_attrs['Description']['Hostname'], address=node_attrs['Status']['Addr']))

        return result

    @inject_param('docker_adapter')
    def _get_nodes_running_service(self, swarm_service, docker_adapter=None):
        running_nodes_ids = [
            task['NodeID']
            for task in docker_adapter.get_swarm_service_tasks(swarm_service)
        ]
        all_nodes = docker_adapter.list_nodes()

        return [
            Node(node.attrs['Description']['Hostname'], node.attrs['Status']['Addr'])
            for node in all_nodes
            if node.attrs['ID'] in running_nodes_ids
        ]

    @inject_param('logger')
    def _get_service_exposed_ports(self, swarm_service, logger=None):
        if 'Ports' in swarm_service.attrs['Endpoint']:
            logger.debug(': %s' % swarm_service.attrs['Endpoint']['Ports'])

        return [
            {"external_port": port['PublishedPort'], "internal_port": port['TargetPort'], "mode": port["PublishMode"]}
            for port in swarm_service.attrs['Endpoint']['Ports']
            if 'PublishedPort' in port
        ] if 'Ports' in swarm_service.attrs['Endpoint'] else []

    @inject_param('logger')
    def _get_swarm_service_labels_and_vars(self, swarm_service, logger=None):
        labels = swarm_service.attrs['Spec']['Labels']
        logger.debug("labels : %s" % labels)
        envs = [
            env
            for env in swarm_service.attrs['Spec']['TaskTemplate']['ContainerSpec']['Env']
        ] if 'Env' in swarm_service.attrs['Spec']['TaskTemplate']['ContainerSpec'] else []

        return labels, envs
