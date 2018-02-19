import unittest

from adapters.docker.docker_adapter import DockerAdapter
from adapters.docker.swarmservice_adapter import SwarmServiceAdapter

from mock import patch

from models import Node, Service

from utils.test_utilities import SwarmNode, SwarmService


class TestSwarmServiceAdapter(unittest.TestCase):
    def setUp(self):
        self.swarmservice_adapter = SwarmServiceAdapter()

    @patch.object(DockerAdapter, 'is_manager', return_value=True)
    @patch.object(
        DockerAdapter,
        'get_swarm_services',
        return_value=['service1']
    )
    @patch.object(SwarmServiceAdapter, '_get_services_object', side_effect=[
        [
            Service(
                name='hello',
                tags=['swarm-service:r1neuke2qg59ivhdblg4dvi7h', 'http'],
                port=30000,
                nodes=[
                    Node(name="node1", address="192.168.50.4"),
                    Node(name="node2", address="192.168.50.5"),
                    Node(name="node3", address="192.168.50.6")
                ]
            )
        ]
    ])
    def test_get_services_on_manager(
        self, mock_get_services_object,
        mock_get_swarm_services, mock_is_manager
    ):
        services = self.swarmservice_adapter.get_services()
        mock_is_manager.assert_called_once()
        mock_get_swarm_services.assert_called_once()
        mock_get_services_object.assert_called_once()
        self.assertEqual(1, len(services))

    @patch.object(DockerAdapter, 'is_manager', return_value=False)
    @patch.object(DockerAdapter, 'get_swarm_services', return_value=None)
    @patch.object(
        SwarmServiceAdapter, '_get_services_object', return_value=None
    )
    def test_get_services_on_worker(
        self, mock_get_services_object,
        mock_get_swarm_services, mock_is_manager
    ):
        services = self.swarmservice_adapter.get_services()
        mock_is_manager.assert_called_once()
        mock_get_swarm_services.assert_not_called()
        mock_get_services_object.assert_not_called()
        self.assertEqual(0, len(services))

    @patch.object(
        SwarmServiceAdapter,
        '_get_service_exposed_ports',
        return_value=[
            {'internal_port': 80, 'external_port': 3000, 'mode': 'ingress'}
        ]
    )
    @patch.object(SwarmServiceAdapter, '_get_nodes_for_service', return_value=[
        Node(name='node1', address='192.168.50.4'),
        Node(name='node2', address='192.168.50.5'),
        Node(name='node3', address='192.168.50.6')
    ])
    @patch.object(
        SwarmServiceAdapter,
        '_get_nodes_running_service',
        return_value=[Node(name='node1', address='192.168.50.4')]
    )
    @patch.object(
        SwarmServiceAdapter,
        '_get_swarm_service_labels_and_vars',
        return_value=[{'service_tags': 'http,https'}, ['service_name=hello']]
    )
    def test_get_services_object(
        self, mock_get_swarm_service_labels_and_vars,
        mock_get_nodes_running_service, mock_get_nodes_for_service,
        mock_get_service_exposed_ports
    ):
        service = SwarmService(
            id='r1neuke2qg59ivhdblg4dvi7h',
            attrs={'Spec': {'Name': 'hello'}}
        )
        services = self.swarmservice_adapter._get_services_object(service)
        self.assertEqual(1, len(services))
        self.assertEqual('hello', services[0].name)
        self.assertEqual(3, len(services[0].nodes))
        self.assertEqual(3, len(services[0].tags))

    @patch.object(
        SwarmServiceAdapter, '_get_service_exposed_ports', return_value=[]
    )
    @patch.object(
        SwarmServiceAdapter, '_get_nodes_for_service', return_value=None
    )
    @patch.object(
        SwarmServiceAdapter,
        '_get_swarm_service_labels_and_vars',
        return_value=None
    )
    def test_get_services_object_no_exposed_ports(
        self, mock_get_swarm_service_labels_and_vars,
        mock_get_nodes_for_service, mock_get_service_exposed_ports
    ):
        service = SwarmService(
            id='r1neuke2qg59ivhdblg4dvi7h',
            attrs={'Spec': {'Name': 'hello'}}
        )
        services = self.swarmservice_adapter._get_services_object(service)
        self.assertEqual(0, len(services))
        mock_get_service_exposed_ports.assert_called_once()
        mock_get_nodes_for_service.assert_not_called()
        mock_get_swarm_service_labels_and_vars.assert_not_called()

    @patch.object(
        SwarmServiceAdapter,
        '_get_service_exposed_ports',
        return_value=[{'internal_port': 80, 'external_port': 3000}]
    )
    @patch.object(
        SwarmServiceAdapter, '_get_nodes_for_service', return_value=[]
    )
    @patch.object(
        SwarmServiceAdapter, '_get_nodes_running_service', return_value=[]
    )
    @patch.object(
        SwarmServiceAdapter,
        '_get_swarm_service_labels_and_vars',
        return_value=None
    )
    def test_get_services_object_no_node(
        self, mock_get_swarm_service_labels_and_vars,
        mock_get_nodes_running_service, mock_get_nodes_for_service,
        mock_get_service_exposed_ports
    ):
        service = SwarmService(
            id='r1neuke2qg59ivhdblg4dvi7h',
            attrs={'Spec': {'Name': 'hello'}}
        )
        services = self.swarmservice_adapter._get_services_object(service)
        self.assertEqual(0, len(services))
        mock_get_service_exposed_ports.assert_called_once()
        mock_get_nodes_for_service.assert_called_once()
        mock_get_swarm_service_labels_and_vars.assert_not_called()

    @patch.object(DockerAdapter, 'list_nodes', return_value=[
        SwarmNode({
            'Status': {'State': 'ready', 'Addr': '192.168.50.4'},
            'Description': {'Hostname': 'node1'}
        }),
        SwarmNode({
            'Status': {'State': 'ready', 'Addr': '192.168.50.5'},
            'Description': {'Hostname': 'node2'}
        }),
        SwarmNode({
            'Status': {'State': 'ready', 'Addr': '192.168.50.6'},
            'Description': {'Hostname': 'node3'}
        }),
        SwarmNode({
            'Status': {'State': 'down', 'Addr': '192.168.50.7'},
            'Description': {'Hostname': 'node4'}
        })
    ])
    def test_get_nodes_for_service(self, mock_list_nodes):
        self.assertEqual(
            3,
            len(self.swarmservice_adapter._get_nodes_for_service(
                SwarmService(id='r1neuke2qg59ivhdblg4dvi7h')
            ))
        )

    def test_get_service_exposed_ports(self):
        exposed_ports = self.swarmservice_adapter._get_service_exposed_ports(
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
            len(self.swarmservice_adapter._get_service_exposed_ports(
                SwarmService(
                    id='r1neuke2qg59ivhdblg4dvi7h',
                    attrs={'Endpoint': {}}
                )
            ))
        )

    def test__get_swarm_service_labels_and_vars(self):
        labels, envs = self.swarmservice_adapter._get_swarm_service_labels_and_vars(
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

    @patch.object(
        DockerAdapter,
        'get_swarm_service_tasks',
        return_value=[{'NodeID': '123456789'}]
    )
    @patch.object(DockerAdapter, 'list_nodes', return_value=[
        SwarmNode({
            'Status': {'State': 'ready', 'Addr': '192.168.50.4'},
            'Description': {'Hostname': 'node1'},
            'ID': '123456789'
        }),
        SwarmNode({
            'Status': {'State': 'ready', 'Addr': '192.168.50.5'},
            'Description': {'Hostname': 'node2'},
            'ID': '45676431467'
        }),
        SwarmNode({
            'Status': {'State': 'ready', 'Addr': '192.168.50.6'},
            'Description': {'Hostname': 'node3'},
            'ID': '5465616974984'
        }),
        SwarmNode({
            'Status': {'State': 'down', 'Addr': '192.168.50.7'},
            'Description': {'Hostname': 'node4'},
            'ID': '46516167491'
        })
    ])
    def test_get_nodes_running_service(self, mock_list_nodes, mock_get_tasks):
        self.assertEqual(
            1,
            len(self.swarmservice_adapter._get_nodes_running_service(
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
            ))
        )
