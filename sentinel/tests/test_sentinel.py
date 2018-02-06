import unittest
from mock import patch
from sentinel import sync, process_event
from adapters.backends.consul import ConsulAdapter
from adapters.orchestrators.swarm import SwarmAdapter
from models import Service, Node


class TestSentinel(unittest.TestCase):

    @patch.object(SwarmAdapter, 'get_service', return_value=[
        Service(name='hello', port=3000, tags=[], nodes=[Node(name="node1", address="192.168.50.4"), Node(name="node2", address="192.168.50.5"), Node(name="node3", address="192.168.50.6")]),
        Service(name='toto', port=3000, tags=[], nodes=[Node(name="node1", address="192.168.50.4")])
    ])
    @patch.object(ConsulAdapter, 'register_service', return_value=None)
    def test_process_event_create(self, mock_register_service, mock_get_services):
        process_event({'Action': 'create'})
        mock_get_services.assert_called_once()
        self.assertEqual(2, mock_register_service.call_count)

    @patch.object(SwarmAdapter, 'get_service', return_value=[])
    @patch.object(ConsulAdapter, 'register_service', return_value=None)
    def test_process_event_create_no_service(self, mock_register_service, mock_get_services):
        process_event({'Action': 'create'})
        mock_get_services.assert_called_once()
        mock_register_service.assert_not_called()

    @patch.object(ConsulAdapter, 'remove_service_with_tag', return_value=None)
    def test_process_event_remove_type_service(self, mock_remove_service_with_tag):
        process_event({'Action': 'remove', 'Type': 'service', 'Actor': {'ID': '123456'}})
        mock_remove_service_with_tag.assert_called_once_with('swarm-service:123456')

    @patch.object(ConsulAdapter, 'remove_service_with_tag', return_value=None)
    def test_process_event_remove_type_container(self, mock_remove_service_with_tag):
        process_event({'Action': 'remove', 'Type': 'container', 'Actor': {'ID': '123456', 'Attributes': {}}})
        mock_remove_service_with_tag.assert_called_once_with('container:123456')

    @patch.object(ConsulAdapter, 'remove_service_with_tag', return_value=None)
    def test_process_event_remove_type_service_container(self, mock_remove_service_with_tag):
        process_event({'Action': 'remove', 'Type': 'container', 'Actor': {'ID': '123456', 'Attributes': {'com.docker.swarm.service.name': 'test'}}})
        mock_remove_service_with_tag.assert_not_called()

    @patch.object(SwarmAdapter, 'process_event', return_value=None)
    def test_process_event_update(self, mock_process_event):
        process_event({'Action': 'update'})
        mock_process_event.assert_called_once()

    @patch.object(ConsulAdapter, 'get_services', return_value=[
        Service(name='hello', port=3000, tags=[], nodes=[Node(name="node1", address="192.168.50.4"), Node(name="node2", address="192.168.50.5"), Node(name="node3", address="192.168.50.6")]),
        Service(name='pets', port=3000, tags=[], nodes=[Node(name="node1", address="192.168.50.4")])
    ])
    @patch.object(SwarmAdapter, 'get_services', return_value=[
        Service(name='hello', port=3000, tags=[], nodes=[Node(name="node1", address="192.168.50.4"), Node(name="node2", address="192.168.50.5"), Node(name="node3", address="192.168.50.6")]),
        Service(name='toto', port=3000, tags=[], nodes=[Node(name="node1", address="192.168.50.4")])
    ])
    @patch.object(ConsulAdapter, 'register_service', return_value=None)
    @patch.object(ConsulAdapter, 'deregister_service', return_value=None)
    def test_sync(self, mock_deregister_service, mock_register_service, mock_swarm_get_services, mock_consul_get_services):
        sync()
        mock_consul_get_services.assert_called_once()
        mock_swarm_get_services.assert_called_once()
        mock_register_service.assert_called_once()
        mock_deregister_service.assert_called_once()
