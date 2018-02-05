import unittest
from mock import patch
from models import Service, Node
from adapters.orchestrators.swarm import SwarmAdapter
from utils.test_utilities import Container, SwarmService


class TestSwarm(unittest.TestCase):
    def setUp(self):
        self.swarm_adapter = SwarmAdapter()

    @patch.object(SwarmAdapter, '_process_node_down', return_value=None)
    @patch.object(SwarmAdapter, '_process_node_up', return_value=None)
    def test_process_event_node_drain(self, mock_process_up, mock_process_down):
        self.swarm_adapter.process_event(
            {
                'Type': 'node',
                'Action': 'update',
                'Actor': {
                    'Attributes': {
                        'availability.new': 'drain',
                        'name': 'node1'
                    }
                }
            }
        )
        mock_process_up.assert_not_called()
        mock_process_down.assert_called_once_with('node1', 'drain')

    @patch.object(SwarmAdapter, '_process_node_down', return_value=None)
    @patch.object(SwarmAdapter, '_process_node_up', return_value=None)
    def test_process_event_node_down(self, mock_process_up, mock_process_down):
        self.swarm_adapter.process_event(
            {
                'Type': 'node',
                'Action': 'update',
                'Actor': {
                    'Attributes': {
                        'state.new': 'down',
                        'name': 'node1'
                    }
                }
            }
        )
        mock_process_up.assert_not_called()
        mock_process_down.assert_called_once_with('node1', 'down')

    @patch.object(SwarmAdapter, '_process_node_down', return_value=None)
    @patch.object(SwarmAdapter, '_process_node_up', return_value=None)
    def test_process_event_node_active(self, mock_process_up, mock_process_down):
        self.swarm_adapter.process_event(
            {
                'Type': 'node',
                'Action': 'update',
                'Actor': {
                    'Attributes': {
                        'availability.new': 'active',
                        'name': 'node1'
                    }
                }
            }
        )
        mock_process_down.assert_not_called()
        mock_process_up.assert_called_once_with('node1', 'active')

    @patch.object(SwarmAdapter, '_process_node_down', return_value=None)
    @patch.object(SwarmAdapter, '_process_node_up', return_value=None)
    def test_process_event_node_ready(self, mock_process_up, mock_process_down):
        self.swarm_adapter.process_event(
            {
                'Type': 'node',
                'Action': 'update',
                'Actor': {
                    'Attributes': {
                        'state.new': 'ready',
                        'name': 'node1'
                    }
                }
            }
        )
        mock_process_down.assert_not_called()
        mock_process_up.assert_called_once_with('node1', 'ready')

    @patch.object(SwarmAdapter, '_is_manager', return_value=True)
    @patch.object(SwarmAdapter, '_get_swarm_services', return_value=['service1'])
    @patch.object(SwarmAdapter, '_get_services_object', side_effect=[
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
    @patch.object(SwarmAdapter, '_get_containers', return_value=[Container('92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04')])
    @patch.object(SwarmAdapter, '_get_services_object_from_container', side_effect=[
        [
            Service(
                name='toto',
                tags=['container:92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04', 'http'],
                port=30001,
                nodes=[
                    Node(name="node3", address="192.168.50.6")
                ]
            )
        ]
    ])
    def test_get_services_on_manager(self, mock_get_services_object_from_container, mock_get_containers, mock_get_services_object, mock_get_swarm_services, mock_is_manager):
        services = self.swarm_adapter.get_services()
        mock_is_manager.assert_called_once()
        mock_get_swarm_services.assert_called_once()
        mock_get_services_object.assert_called_once()
        mock_get_containers.assert_called_once()
        mock_get_services_object_from_container.assert_called_once()
        self.assertEqual(2, len(services))

    @patch.object(SwarmAdapter, '_is_manager', return_value=False)
    @patch.object(SwarmAdapter, '_get_swarm_services', return_value=None)
    @patch.object(SwarmAdapter, '_get_services_object', return_value=None)
    @patch.object(SwarmAdapter, '_get_containers', return_value=[Container('92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04')])
    @patch.object(SwarmAdapter, '_get_services_object_from_container', side_effect=[
        [
            Service(
                name='toto',
                tags=['container:92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04', 'http'],
                port=30001,
                nodes=[
                    Node(name="node3", address="192.168.50.6")
                ]
            )
        ]
    ])
    def test_get_services_on_worker(self, mock_get_services_object_from_container, mock_get_containers, mock_get_services_object, mock_get_swarm_services, mock_is_manager):
        services = self.swarm_adapter.get_services()
        mock_is_manager.assert_called_once()
        mock_get_swarm_services.assert_not_called()
        mock_get_services_object.assert_not_called()
        mock_get_containers.assert_called_once()
        mock_get_services_object_from_container.assert_called_once()
        self.assertEqual(1, len(services))

    @patch.object(SwarmAdapter, '_is_manager', return_value=None)
    @patch.object(SwarmAdapter, '_get_services_object', return_value=None)
    @patch.object(SwarmAdapter, '_get_services_object_from_container', side_effect=[
        [
            Service(
                name='toto',
                tags=['container:92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04', 'http'],
                port=30001,
                nodes=[
                    Node(name="node3", address="192.168.50.6")
                ]
            )
        ]
    ])
    def test_get_service_container(self, mock_get_services_object_from_container, mock_get_services_object, mock_is_manager):
        services = self.swarm_adapter.get_service(
            {
                'Type': 'container',
                'Actor': {'ID': '92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04'}
            }
        )
        mock_get_services_object_from_container.assert_called_once()
        mock_get_services_object.assert_not_called()
        mock_is_manager.assert_not_called()
        self.assertEqual(1, len(services))

    @patch.object(SwarmAdapter, '_is_manager', return_value=False)
    @patch.object(SwarmAdapter, '_get_services_object', return_value=None)
    @patch.object(SwarmAdapter, '_get_services_object_from_container', return_value=None)
    def test_get_service_no_manager(self, mock_get_services_object_from_container, mock_get_services_object, mock_is_manager):
        services = self.swarm_adapter.get_service({'Type': 'service', 'Actor': {'ID': '92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04'}})
        mock_is_manager.assert_called_once()
        mock_get_services_object.assert_not_called()
        mock_get_services_object_from_container.assert_not_called()
        self.assertEqual(0, len(services))

    @patch.object(SwarmAdapter, '_is_manager', return_value=True)
    def test_get_service_tag_to_remove(self, mock_is_manager):
        tag = self.swarm_adapter.get_service_tag_to_remove(
            {
                'Type': 'service',
                'Actor': {'ID': '92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04'}
            }
        )

        self.assertEqual('swarm-service:92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04', tag)

    @patch.object(SwarmAdapter, '_is_manager', return_value=True)
    def test_get_service_tag_to_remove_container(self, mock_is_manager):
        tag = self.swarm_adapter.get_service_tag_to_remove(
            {
                'Type': 'container',
                'Actor': {'ID': '92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04'}
            }
        )

        self.assertEqual('container:92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04', tag)

    @patch.object(SwarmAdapter, '_is_manager', return_value=False)
    def test_get_service_tag_to_remove_container(self, mock_is_manager):
        tag = self.swarm_adapter.get_service_tag_to_remove(
            {
                'Type': 'service',
                'Actor': {'ID': '92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04'}
            }
        )

        self.assertEqual(None, tag)

    @patch.object(SwarmAdapter, '_get_service_exposed_ports', return_value=[{'internal_port': 80, 'external_port': 3000}])
    @patch.object(SwarmAdapter, '_get_nodes_for_service', return_value=[
        Node(name='node1', address='192.168.50.4'),
        Node(name='node2', address='192.168.50.5'),
        Node(name='node3', address='192.168.50.6')
    ])
    @patch.object(SwarmAdapter, '_get_swarm_service_labels_and_vars', return_value=[[{'service_tags': 'http,https'}, {'service_name': 'hello'}], ['service_name=hello', 'service_tags=http,https']])
    def test_get_services_object(self, mock_get_swarm_service_labels_and_vars, mock_get_nodes_for_service, mock_get_service_exposed_ports):
        service = SwarmService(id='r1neuke2qg59ivhdblg4dvi7h', attrs={'Spec': {'Name': 'hello'}})
        services = self.swarm_adapter._get_services_object(service)
        self.assertEqual(1, len(services))
        self.assertEqual('hello', services[0].name)
        self.assertEqual(3, len(services[0].nodes))
        self.assertEqual(3, len(services[0].tags))

    @patch.object(SwarmAdapter, '_get_service_exposed_ports', return_value=[])
    @patch.object(SwarmAdapter, '_get_nodes_for_service', return_value=None)
    @patch.object(SwarmAdapter, '_get_swarm_service_labels_and_vars', return_value=None)
    def test_get_services_object_no_exposed_ports(self, mock_get_swarm_service_labels_and_vars, mock_get_nodes_for_service, mock_get_service_exposed_ports):
        service = SwarmService(id='r1neuke2qg59ivhdblg4dvi7h', attrs={'Spec': {'Name': 'hello'}})
        services = self.swarm_adapter._get_services_object(service)
        self.assertEqual(0, len(services))
        mock_get_service_exposed_ports.assert_called_once()
        mock_get_nodes_for_service.assert_not_called()
        mock_get_swarm_service_labels_and_vars.assert_not_called()

    @patch.object(SwarmAdapter, '_get_service_exposed_ports', return_value=[{'internal_port': 80, 'external_port': 3000}])
    @patch.object(SwarmAdapter, '_get_nodes_for_service', return_value=[])
    @patch.object(SwarmAdapter, '_get_swarm_service_labels_and_vars', return_value=None)
    def test_get_services_object_no_node(self, mock_get_swarm_service_labels_and_vars, mock_get_nodes_for_service, mock_get_service_exposed_ports):
        service = SwarmService(id='r1neuke2qg59ivhdblg4dvi7h', attrs={'Spec': {'Name': 'hello'}})
        services = self.swarm_adapter._get_services_object(service)
        self.assertEqual(0, len(services))
        mock_get_service_exposed_ports.assert_called_once()
        mock_get_nodes_for_service.assert_called_once()
        mock_get_swarm_service_labels_and_vars.assert_not_called()
