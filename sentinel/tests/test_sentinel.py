import unittest
from mock import patch
from sentinel import sync
from backends.consul import Consul
from orchestrators.swarm import Swarm
from models import Service, Node


class TestSentinel(unittest.TestCase):

    # @patch.object(Swarm, 'get_service', return_value=[
    #     Service(name='hello', port=3000, tags=[], nodes=[Node(name="node1", address="192.168.50.4"), Node(name="node2", address="192.168.50.5"), Node(name="node3", address="192.168.50.6")]),
    #     Service(name='toto', port=3000, tags=[], nodes=[Node(name="node1", address="192.168.50.4")])
    # ])
    # @patch.object(Consul, 'register_service', return_value=None)
    # def test_process_event_create(self, mock_register_service, mock_get_services):
    #     process_event({'Action': 'create'})
    #     mock_get_services.assert_called_once()
    #     self.assertEqual(2, mock_register_service.call_count)

    # @patch.object(Swarm, 'get_service', return_value=[])
    # @patch.object(Consul, 'register_service', return_value=None)
    # def test_process_event_create_no_service(self, mock_register_service, mock_get_services):
    #     process_event({'Action': 'create'})
    #     mock_get_services.assert_called_once()
    #     mock_register_service.assert_not_called()

    # @patch.object(DockerAdapter, 'is_manager', return_value=True)
    # @patch.object(Consul, 'remove_service_with_tag', return_value=None)
    # def test_process_event_remove_type_service(self, mock_remove_service_with_tag, mock_swarm_is_manager):
    #     process_event({'Action': 'remove', 'Type': 'service', 'Actor': {'ID': '123456'}})
    #     mock_remove_service_with_tag.assert_called_once_with('swarm-service:123456')

    # @patch.object(DockerAdapter, 'is_manager', return_value=False)
    # @patch.object(Consul, 'remove_service_with_tag', return_value=None)
    # def test_process_event_remove_type_service_not_manager(self, mock_remove_service_with_tag, mock_swarm_is_manager):
    #     process_event({'Action': 'remove', 'Type': 'service', 'Actor': {'ID': '123456'}})
    #     mock_remove_service_with_tag.assert_not_called()

    # @patch.object(Consul, 'remove_service_with_tag', return_value=None)
    # def test_process_event_remove_type_container(self, mock_remove_service_with_tag):
    #     process_event({'Action': 'remove', 'Type': 'container', 'Actor': {'ID': '123456', 'Attributes': {}}})
    #     mock_remove_service_with_tag.assert_called_once_with('container:123456')

    # @patch.object(Consul, 'remove_service_with_tag', return_value=None)
    # def test_process_event_remove_type_service_container(self, mock_remove_service_with_tag):
    #     process_event({'Action': 'remove', 'Type': 'container', 'Actor': {'ID': '123456', 'Attributes': {'com.docker.swarm.service.name': 'test'}}})
    #     mock_remove_service_with_tag.assert_not_called()

    # @patch.object(Swarm, 'process_event', return_value=None)
    # def test_process_event_update(self, mock_process_event):
    #     process_event({'Action': 'update'})
    #     mock_process_event.assert_called_once()

    @patch.object(Consul, 'get_services', return_value=[
        Service(name='hello', port=3000, tags=[], nodes=[Node(name="node1", address="192.168.50.4"), Node(name="node2", address="192.168.50.5"), Node(name="node3", address="192.168.50.6")]),
        Service(name='pets', port=3000, tags=[], nodes=[Node(name="node1", address="192.168.50.4")])
    ])
    @patch.object(Swarm, 'get_services', return_value=[
        Service(name='hello', port=3000, tags=[], nodes=[Node(name="node1", address="192.168.50.4"), Node(name="node2", address="192.168.50.5"), Node(name="node3", address="192.168.50.6")]),
        Service(name='toto', port=3000, tags=[], nodes=[Node(name="node1", address="192.168.50.4")])
    ])
    @patch.object(Consul, 'register_service', return_value=None)
    @patch.object(Consul, 'deregister_service', return_value=None)
    def test_sync(self, mock_deregister_service, mock_register_service, mock_swarm_get_services, mock_consul_get_services):
        sync()
        mock_consul_get_services.assert_called_once()
        mock_swarm_get_services.assert_called_once()
        mock_register_service.assert_called_once()
        mock_deregister_service.assert_called_once()
