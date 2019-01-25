from discovery.layers.domain.adapter.docker import DockerAdapter


class SwarmAdapter(DockerAdapter):
    """Adapter to request docker swarm API
    """

    def list_nodes(self):
        return self.client.nodes.list()

    def get_local_node_address(self):
        # To define if not swarm
        return self.client.info()['Swarm']['NodeAddr']

    def is_manager(self):
        return self.client.info()['Swarm']['ControlAvailable']

    @staticmethod
    def is_ready(swarmnode):
        return swarmnode.attrs['Status']['State'] == 'ready'

    def get_swarmservice_networks(self, swarmservice):
        networks = [
            self.get_network_from_id(network['Target'])
            for network in swarmservice.attrs['Spec']['TaskTemplate']['Networks']
        ] if 'Networks' in swarmservice.attrs['Spec']['TaskTemplate'] else []
        return networks

    def get_swarm_services(self):
        """
        Returns:
            list of :py:class:`from Docker.Models.services import Service`: The services.
        """
        return self.client.services.list()

    def get_swarm_services_from_filters(self, filters: dict) ->list:
        return self.client.services.list(filters=filters)

    def get_swarm_service_by_id(self, service_id):
        return self.client.services.get(service_id)

    @staticmethod
    def get_swarm_service_tasks(swarm_service):
        return swarm_service.tasks()

    @staticmethod
    def get_swarmservice_name(swarm_service):
        return swarm_service.attrs['Spec']['Name']

    @staticmethod
    def get_swarmnode_id(swarmnode):
        return swarmnode.attrs['ID']

    @staticmethod
    def get_swarmnode_name(swarmnode):
        return swarmnode.attrs['Description']['Hostname']

    @staticmethod
    def get_swarmnode_address(swarmnode):
        return swarmnode.attrs['Status']['Addr']

    @staticmethod
    def get_swarmservice_exposed_ports(swarmservice):
        return [
            {
                "external_port": port['PublishedPort'],
                "internal_port": port['TargetPort'],
                "mode": port["PublishMode"]
            }
            for port in swarmservice.attrs['Endpoint']['Ports']
            if 'PublishedPort' in port
        ] if 'Ports' in swarmservice.attrs['Endpoint'] else []

    @staticmethod
    def get_swarmservice_labels_and_vars(swarmservice):
        labels = swarmservice.attrs['Spec']['Labels']
        envs = [
            env
            for env in swarmservice.attrs['Spec']['TaskTemplate']['ContainerSpec']['Env']
        ] if 'Env' in swarmservice.attrs['Spec']['TaskTemplate']['ContainerSpec'] else []

        return labels, envs
