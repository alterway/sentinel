import os
from docker.client import DockerClient
from ddd_domain_driven_design.domain.utils.multiton import Multiton


class DockerAdapter(metaclass=Multiton):
    """Adapter to request docker API
    """

    def __init__(self):
        self._client = DockerAdapter.get_docker_socket()

        # all_c = self.client.containers.list(all=False, filters={"label": "com.docker.swarm.service.id=mkw5pjmv3e0irdfnlgbfufo9y"})
        # all_s = self.client.services.list(filters={"label": "com.docker.swarm.service.id=mkw5pjmv3e0irdfnlgbfufo9y"})
        # node = self.client.nodes.get("sxmltdhnozd26b42za0fxq480")
        # info=self.client.info()

        self._node_name = self.client.info()['Name']
        self._node_id = self.client.info()['Swarm']['NodeID']

    @property
    def client(self) -> DockerClient:
        """
            service client

            :type self: DockerAdapter
            :rtype: DockerClient
        """
        return self._client

    @staticmethod
    def get_docker_socket():
        return DockerClient(
            base_url='unix://var/run/docker.sock',
            version='auto'
        )

    def get_version(self):
        return '_'.join(
            self.client.version()['Version'].split('-')[0].split('.')[0:2]
        )

    def list_container(self):
        return self.client.containers.list()

    def get_container_from_id(self, container_id):
        return self.client.containers.get(container_id)

    def get_containers_from_filters(self, filters: dict) ->list:
        return self.client.containers.list(filters=filters)

    @staticmethod
    def container_is_running(container):
        return container.status == "running"

    @staticmethod
    def container_is_not_swarmservice(container):
        return 'com.docker.swarm.service.id' not in container.attrs['Config']['Labels']

    @staticmethod
    def get_container_name(container):
        if 'com.docker.compose.service' in container.attrs['Config']['Labels']:
            return container.attrs['Config']['Labels']['com.docker.compose.service']

        return container.attrs['Name'].replace('/', '')

    @staticmethod
    def get_container_exposed_ports(container):
        ports = []
        for key in container.attrs['NetworkSettings']['Ports'].keys():
            if container.attrs['NetworkSettings']['Ports'][key] \
                    and container.attrs['NetworkSettings']['Ports'][key][0]['HostPort']:
                ports.append({
                    'internal_port': int(key.replace('/tcp', '').replace('/udp', '')),
                    'external_port': int(container.attrs['NetworkSettings']['Ports'][key][0]['HostPort'])
                })

        return ports

    @staticmethod
    def get_container_labels_and_vars(container):
        labels = container.attrs['Config']['Labels']
        envs = [
            env
            for env in container.attrs['Config']['Env']
        ] if 'Env' in container.attrs['Config'] else []

        return labels, envs

    def get_local_node_name(self):
        return self._node_name

    def get_local_node_id(self):
        return self._node_id

    @classmethod
    def get_local_node_address(cls, address=None):
        return os.environ.get("LOCAL_IP_ADDRESS") if os.environ.get("LOCAL_IP_ADDRESS") else address

    def get_local_node_from_id(self, node_id):
        return self.client.nodes.get(node_id)

    def get_local_node_from_name(self, node_name):
        return self.client.nodes.list(filters={'name': node_name})

    def get_networks(self):
        return self.client.networks.list()

    def get_network_from_id(self, network_id):
        return self.client.networks.get(network_id)
