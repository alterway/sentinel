import docker


class DockerAdapter():
    """Adapter to request docker API
    """
    @classmethod
    def get_local_node_name(cls):
        client = cls._get_docker_socket()
        return client.info()['Name']

    @classmethod
    def get_local_node_address(cls):
        client = cls._get_docker_socket()
        return client.info()['Swarm']['NodeAddr']

    @classmethod
    def list_nodes(cls):
        client = cls._get_docker_socket()
        return client.nodes.list()

    @classmethod
    def list_container(cls):
        client = cls._get_docker_socket()
        return client.containers.list()

    @classmethod
    def get_swarm_service_by_id(cls, service_id):
        client = cls._get_docker_socket()
        return client.services.get(service_id)

    @classmethod
    def get_container_from_id(cls, container_id):
        client = cls._get_docker_socket()
        return client.containers.get(container_id)

    @classmethod
    def is_manager(cls):
        client = cls._get_docker_socket()
        return client.info()['Swarm']['ControlAvailable']

    @classmethod
    def get_swarm_services(cls):
        client = cls._get_docker_socket()
        return client.services.list()

    @staticmethod
    def get_swarm_service_tasks(swarm_service):
        return swarm_service.tasks()

    @staticmethod
    def _get_docker_socket():
        return docker.DockerClient(
            base_url='unix://var/run/docker.sock',
            version='auto'
        )
