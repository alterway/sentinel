from utils.dependencies_injection import inject_param
from service.service_base import ServiceBase
from models import Node, Service
from exceptions import InvalidIPAddress


class SwarmService(ServiceBase):
    """ Adaper to manage docker swarm service as service
    """

    @classmethod
    @inject_param('swarm_adapter')
    def get_services(cls, swarm_adapter=None):
        services = []

        # If manager get swarm services
        if swarm_adapter.is_manager():
            swarm_services = swarm_adapter.get_swarm_services()

            for service in swarm_services:
                services.extend(cls._get_services_object(service))

        return services

    @classmethod
    @inject_param('swarm_adapter')
    def get_services_from_id(cls, service_id, swarm_adapter=None):
        if swarm_adapter.is_manager():
            return cls._get_services_object(swarm_adapter.get_swarm_service_by_id(service_id))
        else:
            return []

    @classmethod
    @inject_param('swarm_adapter')
    @inject_param('logger')
    def _get_services_object(cls, service, swarm_adapter=None, logger=None):
        exposed_ports = swarm_adapter.get_swarmservice_exposed_ports(service)
        services = []
        if len(exposed_ports) == 0:
            logger.info('Ignored Service : %s don\'t publish port' % swarm_adapter.get_swarmservice_name(service))
        else:
            all_nodes = cls._get_all_nodes()
            running_nodes = cls._get_nodes_running_service(service)
            if len(all_nodes) == 0 and len(running_nodes) == 0:
                logger.info('Ignored Service: %s don\'t run in available host' % swarm_adapter.get_swarmservice_name(service))
            else:
                tags = ['swarm-service:%s' % service.id]
                labels, envs = swarm_adapter.get_swarmservice_labels_and_vars(service)
                for port in exposed_ports:
                    if cls._has_to_be_registred(labels, envs, port['internal_port']):
                        tags.extend(cls._get_tags(labels, envs, port['internal_port']))
                        name = cls._get_name_from_label_and_envs(labels, envs, port['internal_port'])
                        services.append(
                            Service(
                                name=name if name is not None else "%s-%s" % (
                                    swarm_adapter.get_swarmservice_name(service),
                                    port['external_port']
                                ),
                                nodes=all_nodes if port['mode'] == 'ingress' else running_nodes,
                                tags=tags,
                                port=port['external_port']
                            )
                        )

            for service in services:
                logger.debug(": %s" % service.__dict__)

        return services

    @classmethod
    @inject_param('swarm_adapter')
    @inject_param('logger')
    def _get_all_nodes(cls, swarm_adapter=None, logger=None):
        all_nodes = []

        for node in swarm_adapter.list_nodes():
            if swarm_adapter.is_ready(node):
                all_nodes = cls._add_node_to_list(all_nodes, node)

        return all_nodes

    @classmethod
    @inject_param('swarm_adapter')
    @inject_param('logger')
    def _get_nodes_running_service(cls, swarm_service, swarm_adapter=None, logger=None):
        running_nodes_ids = [
            task['NodeID']
            for task in swarm_adapter.get_swarm_service_tasks(swarm_service)
            if 'NodeID' in task
        ]
        logger.debug('SwarmService - Nodes ID running service are %s' % running_nodes_ids)
        all_nodes = swarm_adapter.list_nodes()
        running_nodes = []
        for node in all_nodes:
            if node.attrs['ID'] in running_nodes_ids and swarm_adapter.is_ready(node):
                running_nodes = cls._add_node_to_list(running_nodes, node)

        logger.debug('SwarmService - Nodes running service are %s' % [
            node.name for node in running_nodes
        ])
        return running_nodes

    @staticmethod
    @inject_param('swarm_adapter')
    @inject_param('logger')
    def _add_node_to_list(node_list, swarmnode_to_add, swarm_adapter=None, logger=None):
        try:
            node_list.append(
                Node(
                    swarm_adapter.get_swarmnode_name(swarmnode_to_add),
                    swarm_adapter.get_swarmnode_address(swarmnode_to_add)
                )
            )
        except InvalidIPAddress as e:
            logger.warning("Can't add node %s : %s" % (
                swarm_adapter.get_swarmnode_name(swarmnode_to_add), e.message)
            )

        return node_list
