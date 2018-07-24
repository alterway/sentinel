import unittest
from mock import patch
from zope.interface.verify import verifyObject


from docker_adapters.swarm_adapter import SwarmAdapter
from service.base import ServiceInterface
from service.swarmservice import SwarmService as SwarmServiceAdapter
from utils.test_utilities import SwarmNode, SwarmService
from models import Node, Service


class TestSwarmService(unittest.TestCase):
    def setUp(self):
        self.swarmservice_adapter = SwarmServiceAdapter()

    def test_service_interface_implementation(self):
        self.assertEqual(True, verifyObject(ServiceInterface, self.swarmservice_adapter))

    @patch.object(SwarmAdapter, 'is_manager', return_value=True)
    @patch.object(
        SwarmAdapter,
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

    @patch.object(SwarmAdapter, 'is_manager', return_value=False)
    @patch.object(SwarmAdapter, 'get_swarm_services', return_value=None)
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
        SwarmAdapter,
        'get_swarmservice_exposed_ports',
        return_value=[
            {'internal_port': 80, 'external_port': 3000, 'mode': 'ingress'}
        ]
    )
    @patch.object(SwarmServiceAdapter, '_get_all_nodes', return_value=[
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
        SwarmAdapter,
        'get_swarmservice_labels_and_vars',
        return_value=[{'service_tags': 'http,https'}, ['service_name=hello']]
    )
    def test_get_services_object(
        self, mock_get_swarm_service_labels_and_vars,
        mock_get_nodes_running_service, mock_get_all_nodes,
        mock_get_service_exposed_ports
    ):
        service = SwarmService(
            service_id='r1neuke2qg59ivhdblg4dvi7h',
            attrs={'Spec': {'Name': 'hello'}}
        )
        services = self.swarmservice_adapter._get_services_object(service)
        self.assertEqual(1, len(services))
        self.assertEqual('hello', services[0].name)
        self.assertEqual(3, len(services[0].nodes))
        self.assertEqual(3, len(services[0].tags))

    @patch.object(
        SwarmAdapter, 'get_swarmservice_exposed_ports', return_value=[]
    )
    @patch.object(
        SwarmServiceAdapter, '_get_all_nodes', return_value=None
    )
    @patch.object(
        SwarmAdapter,
        'get_swarmservice_labels_and_vars',
        return_value=None
    )
    def test_get_services_object_no_exposed_ports(
        self, mock_get_swarm_service_labels_and_vars,
        mock_get_all_nodes, mock_get_service_exposed_ports
    ):
        service = SwarmService(
            service_id='r1neuke2qg59ivhdblg4dvi7h',
            attrs={'Spec': {'Name': 'hello'}}
        )
        services = self.swarmservice_adapter._get_services_object(service)
        self.assertEqual(0, len(services))
        mock_get_service_exposed_ports.assert_called_once()
        mock_get_all_nodes.assert_not_called()
        mock_get_swarm_service_labels_and_vars.assert_not_called()

    @patch.object(
        SwarmAdapter,
        'get_swarmservice_exposed_ports',
        return_value=[{'internal_port': 80, 'external_port': 3000}]
    )
    @patch.object(
        SwarmServiceAdapter, '_get_all_nodes', return_value=[]
    )
    @patch.object(
        SwarmServiceAdapter, '_get_nodes_running_service', return_value=[]
    )
    @patch.object(
        SwarmAdapter,
        'get_swarmservice_labels_and_vars',
        return_value=None
    )
    def test_get_services_object_no_node(
        self, mock_get_swarm_service_labels_and_vars,
        mock_get_nodes_running_service, mock_get_all_nodes,
        mock_get_service_exposed_ports
    ):
        service = SwarmService(
            service_id='r1neuke2qg59ivhdblg4dvi7h',
            attrs={'Spec': {'Name': 'hello'}}
        )
        services = self.swarmservice_adapter._get_services_object(service)
        self.assertEqual(0, len(services))
        mock_get_service_exposed_ports.assert_called_once()
        mock_get_all_nodes.assert_called_once()
        mock_get_swarm_service_labels_and_vars.assert_not_called()

    @patch.object(SwarmAdapter, 'list_nodes', return_value=[
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
        }),
        SwarmNode({
            'Status': {'State': 'ready', 'Addr': '0.0.0.0'},
            'Description': {'Hostname': 'node5'}
        })
    ])
    def test_get_all_nodes(self, mock_list_nodes):
        self.assertEqual(
            3,
            len(self.swarmservice_adapter._get_all_nodes())
        )

    @patch.object(
        SwarmAdapter,
        'get_swarm_service_tasks',
        return_value=[
            {'NodeID': '123456789'},
            {'NodeID': '87456146741'},
            {'NodeID': '46516167491'}
        ]
    )
    @patch.object(SwarmAdapter, 'list_nodes', return_value=[
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
        }),
        SwarmNode({
            'Status': {'State': 'ready', 'Addr': '0.0.0.0'},
            'Description': {'Hostname': 'node5'},
            'ID': '87456146741'
        })
    ])
    def test_get_nodes_running_service(self, mock_list_nodes, mock_get_tasks):
        self.assertEqual(
            1,
            len(self.swarmservice_adapter._get_nodes_running_service(
                SwarmService(
                    service_id="123456789",
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
