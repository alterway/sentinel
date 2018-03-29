from docker_adapters.docker_adapter import DockerAdapter


class SwarmAdapter(DockerAdapter):

    @classmethod
    def list_nodes(cls):
        client = cls.get_docker_socket()
        return client.nodes.list()

    @classmethod
    def get_local_node_address(cls):
        # To define if not swarm
        client = cls.get_docker_socket()
        return client.info()['Swarm']['NodeAddr']

    @classmethod
    def get_swarmservice_by_id(cls, service_id):
        client = cls.get_docker_socket()
        return client.services.get(service_id)

    @classmethod
    def is_manager(cls):
        client = cls.get_docker_socket()
        return client.info()['Swarm']['ControlAvailable']

    @staticmethod
    def is_ready(swarmnode):
        return swarmnode.attrs['Status']['State'] == 'ready'

    @classmethod
    def get_swarm_services(cls):
        client = cls.get_docker_socket()
        return client.services.list()

    @staticmethod
    def get_swarm_service_tasks(swarm_service):
        return swarm_service.tasks()

    @staticmethod
    def get_swarmservice_name(swarm_service):
        return swarm_service.attrs['Spec']['Name']

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
