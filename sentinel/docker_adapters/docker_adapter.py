import docker
import os


class DockerAdapter():
    """Adapter to request docker API
    """
    @classmethod
    def get_version(cls):
        client = cls.get_docker_socket()
        return '_'.join(
            client.version()['Version'].split('-')[0].split('.')[0:2]
        )

    @staticmethod
    def get_docker_socket():
        return docker.DockerClient(
            base_url='unix://var/run/docker.sock',
            version='auto'
        )

    @classmethod
    def get_local_node_name(cls):
        client = cls.get_docker_socket()
        return client.info()['Name']

    @classmethod
    def get_local_node_address(cls):
        return os.environ.get('LOCAL_IP_ADDRESS')

    @classmethod
    def list_container(cls):
        client = cls.get_docker_socket()
        return client.containers.list()

    @classmethod
    def get_container_from_id(cls, container_id):
        client = cls.get_docker_socket()
        return client.containers.get(container_id)

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
        else:
            return container.attrs['Name'].replace('/', '')

    @staticmethod
    def get_container_exposed_ports(container):
        ports = []
        for key in container.attrs['NetworkSettings']['Ports'].keys():
            if container.attrs['NetworkSettings']['Ports'][key] is not None and len(container.attrs['NetworkSettings']['Ports'][key][0]['HostPort']) != 0:
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
