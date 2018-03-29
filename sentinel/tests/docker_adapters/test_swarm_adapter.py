from docker_adapters.swarm_adapter import SwarmAdapter
from utils.test_utilities import SwarmService, SwarmNode, StubDockerSocket
from mock import patch
import unittest


class SwarmAdapterTest(unittest.TestCase):

    def setUp(self):
        self.docker_adapter = SwarmAdapter

    @patch.object(SwarmAdapter, "get_docker_socket", return_value=StubDockerSocket())
    def test_get_local_node_address(self, mock_docker_socket):
        self.assertEqual(
            "192.168.50.5",
            self.docker_adapter.get_local_node_address()
        )

    @patch.object(SwarmAdapter, "get_docker_socket", return_value=StubDockerSocket())
    def test_is_manager_true(self, mock_docker_socket):
        self.assertEqual(
            True,
            self.docker_adapter.is_manager()
        )

    @patch.object(SwarmAdapter, "get_docker_socket", return_value=StubDockerSocket(is_manager=False))
    def test_is_manager_false(self, mock_docker_socket):
        self.assertEqual(
            False,
            self.docker_adapter.is_manager()
        )

    def test_is_ready_true(self):
        self.assertEqual(
            True,
            self.docker_adapter.is_ready(
                SwarmNode(
                    {
                        "Status": {"State": "ready"}
                    }
                )
            )
        )

    def test_is_ready_false(self):
        self.assertEqual(
            False,
            self.docker_adapter.is_ready(
                SwarmNode(
                    {
                        "Status": {"State": "down"}
                    }
                )
            )
        )

    def test_get_swarmservice_name(self):
        self.assertEqual(
            "hello",
            self.docker_adapter.get_swarmservice_name(
                SwarmService(
                    id="4841631984961",
                    attrs={
                        "Spec": {"Name": "hello"}
                    }
                )
            )
        )

    def test_get_swarmnode_name(self):
        self.assertEqual(
            "node1",
            self.docker_adapter.get_swarmnode_name(
                SwarmNode(
                    {
                        "Description": {"Hostname": "node1"}
                    }
                )
            )
        )

    def test_get_swarmnode_address(self):
        self.assertEqual(
            "192.168.50.6",
            self.docker_adapter.get_swarmnode_address(
                SwarmNode(
                    {
                        "Status": {"Addr": "192.168.50.6"}
                    }
                )
            )
        )

    def test__get_swarm_service_labels_and_vars(self):
        labels, envs = self.docker_adapter.get_swarmservice_labels_and_vars(
            SwarmService(
                id="123456789",
                attrs={
                    "Spec": {
                        "Labels": {"label1": "aaaa", "label2": "bbbb"},
                        "TaskTemplate": {
                            "ContainerSpec": {
                                "Env": ["env1=myenv1", "env2=myenv2"]
                            }
                        }
                    }
                }
            )
        )
        self.assertEqual({"label1": "aaaa", "label2": "bbbb"}, labels)
        self.assertEqual(["env1=myenv1", "env2=myenv2"], envs)

    def test_get_service_exposed_ports(self):
        exposed_ports = self.docker_adapter.get_swarmservice_exposed_ports(
            SwarmService(
                id='r1neuke2qg59ivhdblg4dvi7h',
                attrs={
                    'Endpoint': {
                        'Ports': [
                            {
                                'PublishedPort': 3000,
                                'TargetPort': 80,
                                'PublishMode': 'ingress'
                            },
                            {
                                'PublishedPort': 3001,
                                'TargetPort': 443,
                                'PublishMode': 'ingress'
                            }
                        ]
                    }
                }
            )
        )
        self.assertEqual(2, len(exposed_ports))
        self.assertEqual(
            [
                {
                    'external_port': 3000,
                    'internal_port': 80,
                    'mode': 'ingress'
                },
                {
                    'external_port': 3001,
                    'internal_port': 443,
                    'mode': 'ingress'
                }
            ],
            sorted(exposed_ports, key=lambda x: x['external_port'])
        )

    def test_get_service_exposed_ports_empty(self):
        self.assertEqual(
            0,
            len(self.docker_adapter.get_swarmservice_exposed_ports(
                SwarmService(
                    id='r1neuke2qg59ivhdblg4dvi7h',
                    attrs={'Endpoint': {}}
                )
            ))
        )
