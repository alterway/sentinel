from docker_adapters.docker_adapter import DockerAdapter
from utils.test_utilities import Container, StubDockerSocket
from mock import patch
import unittest


class DockerAdapterTest(unittest.TestCase):

    def setUp(self):
        self.docker_adapter = DockerAdapter

    @patch.object(DockerAdapter, "get_docker_socket", return_value=StubDockerSocket())
    def test_get_version(self, mock_docker_socket):
        self.assertEqual('18_03', self.docker_adapter.get_version())

    @patch.object(DockerAdapter, "get_docker_socket", return_value=StubDockerSocket())
    def test_get_local_node_name(self, mock_docker_socket):
        self.assertEqual('node1', self.docker_adapter.get_local_node_name())

    def test_get_local_node_address(self):
        self.assertEqual("192.168.50.4", self.docker_adapter.get_local_node_address())

    def test_container_is_running_true(self):
        self.assertEqual(
            True,
            self.docker_adapter.container_is_running(
                Container(
                    id="123456789",
                    attrs={
                        'State': {'Status': 'running'},
                        'Name': '/toto',
                        'Config': {
                            'Labels': {
                                'com.docker.compose.service': 'project_toto'
                            }
                        }
                    }
                )
            )
        )

    def test_container_is_running_false(self):
        self.assertEqual(
            False,
            self.docker_adapter.container_is_running(
                Container(
                    id="123456789",
                    attrs={
                        'State': {'Status': 'created'},
                        'Name': '/toto',
                        'Config': {
                            'Labels': {
                                'com.docker.compose.service': 'project_toto'
                            }
                        }
                    }
                )
            )
        )

    def test_container_is_not_swarmservice_true(self):
        self.assertEqual(
            True,
            self.docker_adapter.container_is_not_swarmservice(
                Container(
                    id="123456789",
                    attrs={
                        'State': {'Status': 'created'},
                        'Name': '/toto',
                        'Config': {
                            'Labels': {}
                        }
                    }
                )
            )
        )

    def test_container_is_not_swarmservice_false(self):
        self.assertEqual(
            False,
            self.docker_adapter.container_is_not_swarmservice(
                Container(
                    id="123456789",
                    attrs={
                        'State': {'Status': 'created'},
                        'Name': '/toto',
                        'Config': {
                            'Labels': {
                                'com.docker.swarm.service.id': 'fafae6f4a6f4a6fa6f4'
                            }
                        }
                    }
                )
            )
        )

    def get_container_name_with_dockercompose(self):
        self.assertEqual(
            'project_toto',
            self.docker_adapter.get_container_name(
                Container(
                    id="123456789",
                    attrs={
                        'State': {'Status': 'created'},
                        'Name': '/toto',
                        'Config': {
                            'Labels': {
                                'com.docker.compose.service': 'project_toto'
                            }
                        }
                    }
                )
            )
        )

    def get_container_name_without_dockercompose(self):
        self.assertEqual(
            'toto',
            self.docker_adapter.get_container_name(
                Container(
                    id="123456789",
                    attrs={
                        'State': {'Status': 'created'},
                        'Name': '/toto',
                        'Config': {
                            'Labels': {}
                        }
                    }
                )
            )
        )

    def test_get_container_exposed_ports(self):
        exposed_ports = self.docker_adapter.get_container_exposed_ports(
            Container(
                id="123456789",
                attrs={
                    "NetworkSettings": {
                        "Ports": {
                            "80/tcp": [{"HostPort": '3000'}],
                            '443/udp': [{'HostPort': '3001'}]
                        }
                    }
                }
            )
        )
        self.assertEqual(2, len(exposed_ports))
        self.assertEqual(
            [
                {'external_port': 3000, 'internal_port': 80},
                {'external_port': 3001, 'internal_port': 443}
            ],
            sorted(exposed_ports, key=lambda x: x['external_port'])
        )

    def test_get_container_exposed_ports_no_port(self):
        exposed_ports = self.docker_adapter.get_container_exposed_ports(
            Container(
                id="123456789",
                attrs={"NetworkSettings": {"Ports": {}}}
            )
        )
        self.assertEqual(0, len(exposed_ports))

    def test_get_container_labels_and_vars(self):
        labels, envs = self.docker_adapter.get_container_labels_and_vars(
            Container(
                id='123456789',
                attrs={
                    "Config": {
                        "Labels": {"label1": "aaaa", "label2": "bbbb"},
                        "Env": ["env1=myenv1", "env2=myenv2"]
                    }
                }
            )
        )
        self.assertEqual({"label1": "aaaa", "label2": "bbbb"}, labels)
        self.assertEqual(["env1=myenv1", "env2=myenv2"], envs)
