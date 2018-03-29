from orchestrators.swarm import Swarm
from docker_adapters.swarm_adapter import SwarmAdapter
from service.container import Container
from service.swarmservice import SwarmService
from backends.consul import Consul
from models import Service, Node
from mock import patch
import unittest


class TestSwarm(unittest.TestCase):
    def setUp(self):
        self.swarm_adapter = Swarm()

    @patch.object(SwarmAdapter, 'is_manager', return_value=True)
    @patch.object(SwarmAdapter, 'get_swarm_services', return_value=['service1'])
    @patch.object(SwarmService, '_get_services_object', side_effect=[
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
    @patch.object(Container, 'get_services', return_value=[
        Service(
            name='toto',
            tags=['container:92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04', 'http'],
            port=30001,
            nodes=[
                Node(name="node3", address="192.168.50.6")
            ]
        )
    ])
    def test_get_services_on_manager(self, mock_get_services, mock_get_services_object, mock_get_swarm_services, mock_is_manager):
        services = self.swarm_adapter.get_services()
        mock_is_manager.assert_called_once()
        mock_get_swarm_services.assert_called_once()
        mock_get_services_object.assert_called_once()
        mock_get_services.assert_called_once()
        self.assertEqual(2, len(services))

    @patch.object(SwarmAdapter, 'is_manager', return_value=False)
    @patch.object(SwarmAdapter, 'get_swarm_services', return_value=None)
    @patch.object(SwarmService, '_get_services_object', return_value=None)
    @patch.object(Container, 'get_services', return_value=[
        Service(
            name='toto',
            tags=['container:92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04', 'http'],
            port=30001,
            nodes=[
                Node(name="node3", address="192.168.50.6")
            ]
        )
    ])
    def test_get_services_on_worker(self, mock_get_services, mock_get_services_object, mock_get_swarm_services, mock_is_manager):
        services = self.swarm_adapter.get_services()
        mock_is_manager.assert_called_once()
        mock_get_swarm_services.assert_not_called()
        mock_get_services_object.assert_not_called()
        mock_get_services.assert_called_once()
        self.assertEqual(1, len(services))

    @patch.object(Swarm, '_process_node_down', return_value=None)
    @patch.object(Swarm, '_process_node_up', return_value=None)
    def test__process_event_node_drain(self, mock_process_up, mock_process_down):
        self.swarm_adapter._process_event(
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

    @patch.object(Swarm, '_process_node_down', return_value=None)
    @patch.object(Swarm, '_process_node_up', return_value=None)
    def test__process_event_node_down(self, mock_process_up, mock_process_down):
        self.swarm_adapter._process_event(
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

    @patch.object(Swarm, '_process_node_down', return_value=None)
    @patch.object(Swarm, '_process_node_up', return_value=None)
    def test__process_event_node_active(self, mock_process_up, mock_process_down):
        self.swarm_adapter._process_event(
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

    @patch.object(Swarm, '_process_node_down', return_value=None)
    @patch.object(Swarm, '_process_node_up', return_value=None)
    def test__process_event_node_ready(self, mock_process_up, mock_process_down):
        self.swarm_adapter._process_event(
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

    @patch.object(Swarm, 'get_service', return_value=[
        Service(name='hello', port=3000, tags=[], nodes=[Node(name="node1", address="192.168.50.4")]),
        Service(name='hello', port=3001, tags=[], nodes=[Node(name="node1", address="192.168.50.4")])
    ])
    @patch.object(Consul, 'remove_service_with_tag', return_value=None)
    @patch.object(Consul, 'register_service', return_value=None)
    def test__process_event_service_update(self, mock_register_service, mock_remove_service, mock_get_service):
        self.swarm_adapter._process_event(
            {"Type": "service", "Action": "update", "Actor": {"ID": "pyqeknfbzwrncs49g79r9967i", "Attributes": {"name": "hello"}}}
        )
        mock_get_service.assert_called_once()
        mock_remove_service.assert_called_once()
        self.assertEqual(2, mock_register_service.call_count)

    @patch.object(SwarmAdapter, 'is_manager', return_value=None)
    @patch.object(SwarmService, '_get_services_object', return_value=None)
    @patch.object(Container, '_get_services_object', side_effect=[
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

    @patch.object(SwarmAdapter, 'is_manager', return_value=False)
    @patch.object(SwarmService, '_get_services_object', return_value=None)
    @patch.object(Container, '_get_services_object', return_value=None)
    def test_get_service_no_manager(self, mock_get_services_object_from_container, mock_get_services_object, mock_is_manager):
        services = self.swarm_adapter.get_service({'Type': 'service', 'Actor': {'ID': '92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04'}})
        mock_is_manager.assert_called_once()
        mock_get_services_object.assert_not_called()
        mock_get_services_object_from_container.assert_not_called()
        self.assertEqual(0, len(services))

    @patch.object(SwarmAdapter, 'is_manager', return_value=True)
    def test_get_service_tag_to_remove(self, mock_is_manager):
        tag = self.swarm_adapter.get_service_tag_to_remove(
            {
                'Type': 'service',
                'Actor': {'ID': '92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04'}
            }
        )

        self.assertEqual('swarm-service:92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04', tag)

    @patch.object(SwarmAdapter, 'is_manager', return_value=True)
    def test_get_service_tag_to_remove_container(self, mock_is_manager):
        tag = self.swarm_adapter.get_service_tag_to_remove(
            {
                'Type': 'container',
                'Actor': {
                    'ID': '92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04',
                    'Attributes': {}
                }
            }
        )

        self.assertEqual('container:92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04', tag)

    @patch.object(SwarmAdapter, 'is_manager', return_value=False)
    def test_get_service_tag_to_remove_container_no_manager(self, mock_is_manager):
        tag = self.swarm_adapter.get_service_tag_to_remove(
            {
                'Type': 'service',
                'Actor': {'ID': '92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04'}
            }
        )

        self.assertEqual(None, tag)
