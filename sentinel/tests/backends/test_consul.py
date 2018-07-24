import unittest
from mock import patch
import requests
from zope.interface.verify import verifyObject
from utils.test_utilities import StubResponse

from models import Service, Node
from backends.backend import Backend
from backends.consul import Consul
from docker_adapters.docker_adapter import DockerAdapter


class TestConsul(unittest.TestCase):

    def setUp(self):
        self.consul_adapter = Consul()

    def test_backend_interface_implementation(self):
        self.assertEqual(True, verifyObject(Backend, self.consul_adapter))

    @patch.object(requests, 'get', side_effect=[
        StubResponse(
            200,
            {
                'consul': [],
                'toto': ['container:92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04'],
                'hello': ['swarm-service:r1neuke2qg59ivhdblg4dvi7h', 'http']
            }
        ),
        StubResponse(
            200,
            [
                {
                    'Address': '192.168.50.4',
                    'ID': 'c7a71046-c0de-c38d-4c90-a7c5c1365978',
                    'Node': 'node1',
                    'ServiceID': 'consul',
                    'ServiceTags': [],
                    'ServiceAddress': '',
                    'ServiceName': 'consul',
                    'ServicePort': 8300
                }, {
                    'Address': '192.168.50.5',
                    'ID': 'b3451590-eb5d-75e9-d7d3-5ecd259af6f9',
                    'Node': 'node2',
                    'ServiceID': 'consul',
                    'ServiceTags': [],
                    'ServiceAddress': '',
                    'ServiceName': 'consul',
                    'ServicePort': 8300
                }, {
                    'Address': '192.168.50.6',
                    'ID': '11d1b97d-0d60-80b8-2097-0080c8742944',
                    'Node': 'node3',
                    'ServiceID': 'consul',
                    'ServiceTags': [],
                    'ServiceAddress': '',
                    'ServiceName': 'consul',
                    'ServicePort': 8300
                }
            ]

        ),
        StubResponse(
            200,
            [
                {
                    'Address': '192.168.50.4',
                    'ID': 'c7a71046-c0de-c38d-4c90-a7c5c1365978',
                    'Node': 'node1',
                    'ServiceID': 'hello-node1',
                    'ServiceTags': ['swarm-service:r1neuke2qg59ivhdblg4dvi7h', 'http'],
                    'ServiceAddress': '192.168.50.4',
                    'ServiceName': 'hello',
                    'ServicePort': 30013
                }, {
                    'Address': '192.168.50.5',
                    'ID': 'b3451590-eb5d-75e9-d7d3-5ecd259af6f9',
                    'Node': 'node2',
                    'ServiceID': 'hello-node2',
                    'ServiceTags': ['swarm-service:r1neuke2qg59ivhdblg4dvi7h', 'http'],
                    'ServiceAddress': '192.168.50.5',
                    'ServiceName': 'hello',
                    'ServicePort': 30013
                }, {
                    'Address': '192.168.50.6',
                    'ID': '11d1b97d-0d60-80b8-2097-0080c8742944',
                    'Node': 'node3',
                    'ServiceID': 'hello-node3',
                    'ServiceTags': ['swarm-service:r1neuke2qg59ivhdblg4dvi7h', 'http'],
                    'ServiceAddress': '192.168.50.6',
                    'ServiceName': 'hello',
                    'ServicePort': 30013
                }
            ]
        ),
        StubResponse(
            200,
            [
                {
                    'Address': '192.168.50.6',
                    'ID': '11d1b97d-0d60-80b8-2097-0080c8742944',
                    'Node': 'node3',
                    'ServiceID': 'toto-node3',
                    'ServiceTags': ['container:92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04'],
                    'ServiceAddress': '192.168.50.6',
                    'ServiceName': 'toto',
                    'ServicePort': 32771
                }
            ]
        )
    ])
    @patch.object(DockerAdapter, 'get_local_node_name', return_value="node1")
    def test_get_services(self, mock_get_local_node_name, mock_get):
        services = self.consul_adapter.get_services()
        self.assertEqual(4, mock_get.call_count)
        mock_get_local_node_name.assert_called_once()
        self.assertEqual(1, len(services))

        services_dict = {}
        for service in services:
            services_dict[service.name] = service

        self.assertEqual(3, len(services_dict['hello'].nodes))
        self.assertEqual(2, len(services_dict['hello'].tags))

    @patch.object(requests, 'put', side_effect=[
        StubResponse(200, True),
        StubResponse(200, True),
        StubResponse(200, True)
    ])
    def test_register_service(self, mock_put):
        service = Service(
            name='hello',
            tags=['swarm-service:r1neuke2qg59ivhdblg4dvi7h', 'http'],
            port=30000,
            nodes=[
                Node(name="node1", address="192.168.50.4"),
                Node(name="node2", address="192.168.50.5"),
                Node(name="node3", address="192.168.50.6")
            ]
        )
        self.consul_adapter.register_service(service)
        self.assertEqual(3, mock_put.call_count)

    @patch.object(requests, 'get', side_effect=[
        StubResponse(
            200,
            {
                'consul': [],
                'toto': ['container:92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04'],
                'hello': ['swarm-service:r1neuke2qg59ivhdblg4dvi7h', 'http']
            }
        ),
        StubResponse(
            200,
            [
                {
                    'Address': '192.168.50.4',
                    'ID': 'c7a71046-c0de-c38d-4c90-a7c5c1365978',
                    'Node': 'node1',
                    'ServiceID': 'consul',
                    'ServiceTags': [],
                    'ServiceAddress': '',
                    'ServiceName': 'consul',
                    'ServicePort': 8300
                }, {
                    'Address': '192.168.50.5',
                    'ID': 'b3451590-eb5d-75e9-d7d3-5ecd259af6f9',
                    'Node': 'node2',
                    'ServiceID': 'consul',
                    'ServiceTags': [],
                    'ServiceAddress': '',
                    'ServiceName': 'consul',
                    'ServicePort': 8300
                }, {
                    'Address': '192.168.50.6',
                    'ID': '11d1b97d-0d60-80b8-2097-0080c8742944',
                    'Node': 'node3',
                    'ServiceID': 'consul',
                    'ServiceTags': [],
                    'ServiceAddress': '',
                    'ServiceName': 'consul',
                    'ServicePort': 8300
                }
            ]

        ),
        StubResponse(
            200,
            [
                {
                    'Address': '192.168.50.4',
                    'ID': 'c7a71046-c0de-c38d-4c90-a7c5c1365978',
                    'Node': 'node1',
                    'ServiceID': 'hello-node1',
                    'ServiceTags': ['swarm-service:r1neuke2qg59ivhdblg4dvi7h', 'http'],
                    'ServiceAddress': '192.168.50.4',
                    'ServiceName': 'hello',
                    'ServicePort': 30013
                }, {
                    'Address': '192.168.50.5',
                    'ID': 'b3451590-eb5d-75e9-d7d3-5ecd259af6f9',
                    'Node': 'node2',
                    'ServiceID': 'hello-node2',
                    'ServiceTags': ['swarm-service:r1neuke2qg59ivhdblg4dvi7h', 'http'],
                    'ServiceAddress': '192.168.50.5',
                    'ServiceName': 'hello',
                    'ServicePort': 30013
                }, {
                    'Address': '192.168.50.6',
                    'ID': '11d1b97d-0d60-80b8-2097-0080c8742944',
                    'Node': 'node3',
                    'ServiceID': 'hello-node3',
                    'ServiceTags': ['swarm-service:r1neuke2qg59ivhdblg4dvi7h', 'http'],
                    'ServiceAddress': '192.168.50.6',
                    'ServiceName': 'hello',
                    'ServicePort': 30013
                }
            ]
        ),
        StubResponse(
            200,
            [
                {
                    'Address': '192.168.50.6',
                    'ID': '11d1b97d-0d60-80b8-2097-0080c8742944',
                    'Node': 'node3',
                    'ServiceID': 'toto-node3',
                    'ServiceTags': ['container:92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04'],
                    'ServiceAddress': '192.168.50.6',
                    'ServiceName': 'toto',
                    'ServicePort': 32771
                }
            ]
        )
    ])
    @patch.object(requests, 'put', side_effect=[
        StubResponse(200, True),
        StubResponse(200, True),
        StubResponse(200, True)
    ])
    @patch.object(DockerAdapter, 'get_local_node_name', return_value="node1")
    def test_remove_service_with_tag(self, mock_get_local_node_name, mock_put, mock_get,):
        self.consul_adapter.remove_service_with_tag('swarm-service:r1neuke2qg59ivhdblg4dvi7h')

        mock_get_local_node_name.assert_called_once()
        self.assertEqual(4, mock_get.call_count)
        self.assertEqual(3, mock_put.call_count)

    @patch.object(requests, 'put', return_value=StubResponse(200, True))
    def test_deregister_node(self, mock_put):
        self.consul_adapter.deregister_node('node1')
        self.assertEqual(1, mock_put.call_count)

    @patch.object(requests, 'put', side_effect=[
        StubResponse(200, True),
        StubResponse(200, True),
        StubResponse(200, True)
    ])
    def test_deregister_service(self, mock_put):
        service = Service(
            name='hello',
            tags=['swarm-service:r1neuke2qg59ivhdblg4dvi7h', 'http'],
            port=30000,
            nodes=[
                Node(name="node1", address="192.168.50.4"),
                Node(name="node2", address="192.168.50.5"),
                Node(name="node3", address="192.168.50.6")
            ]
        )
        self.consul_adapter.deregister_service(service)
        self.assertEqual(3, mock_put.call_count)
