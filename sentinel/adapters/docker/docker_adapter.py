import docker


class DockerAdapter():
    """Adapter to request docker API
    """
    def get_local_node_name(self):
        client = self._get_docker_socket()
        return client.info()['Name']

    def get_local_node_address(self):
        client = self._get_docker_socket()
        return client.info()['Swarm']['NodeAddr']

    def list_nodes(self):
        client = self._get_docker_socket()
        return client.nodes.list()

    def list_container(self):
        client = self._get_docker_socket()
        return client.containers.list()

    def get_swarm_service_by_id(self, service_id):
        client = self._get_docker_socket()
        return client.services.get(service_id)

    def get_container_from_id(self, container_id):
        client = self._get_docker_socket()
        return client.containers.get(container_id)

    def is_manager(self):
        client = self._get_docker_socket()
        return client.info()['Swarm']['ControlAvailable']

    def get_swarm_services(self):
        client = self._get_docker_socket()
        return client.services.list()

    def get_swarm_service_tasks(self, swarm_service):
        return swarm_service.tasks()

    def _get_docker_socket(self):
        return docker.DockerClient(
            base_url='unix://var/run/docker.sock',
            version='auto'
        )
