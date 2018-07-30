import docker
import os


class DockerAdapter(object):
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

        return container.attrs['Name'].replace('/', '')

    @staticmethod
    def get_container_exposed_ports(container):
        ports = []
        for key in container.attrs['NetworkSettings']['Ports'].keys():
            if container.attrs['NetworkSettings']['Ports'][key] and container.attrs['NetworkSettings']['Ports'][key][0]['HostPort']:
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

