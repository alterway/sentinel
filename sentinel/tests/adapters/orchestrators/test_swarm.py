import unittest
from mock import patch
from models import Service, Node
from adapters.orchestrators.swarm import SwarmAdapter
from utils.test_utilities import Container, SwarmService, SwarmNode


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
    @patch.object(SwarmAdapter, '_get_swarm_service_labels_and_vars', return_value=[{'service_tags': 'http,https'}, ['service_name=hello']])
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

    @patch.object(SwarmAdapter, '_get_container_from_id', return_value=Container(
        id='92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04',
        attrs={
            'State': {'Status': 'running'},
            'Name': '/toto',
            'Config': {
                'Labels': {
                    'com.docker.compose.service': 'project_toto'
                }
            }
        }
    ))
    @patch.object(SwarmAdapter, '_get_container_exposed_ports', return_value=[{'internal_port': 80, 'external_port': 3000}])
    @patch.object(SwarmAdapter, '_get_container_labels_and_vars', return_value=[{"service_tags": 'http,https'}, ['service_name=toto']])
    @patch.object(SwarmAdapter, '_get_local_node_name', return_value='node1')
    @patch.object(SwarmAdapter, '_get_local_node_address', return_value='192.168.50.4')
    def test_get_services_object_from_container(self, mock_get_local_node_address, mock_get_local_node_name, mock__get_container_labels_and_vars, mock_get_container_exposed_ports, mock_get_container_from_id):
        services = self.swarm_adapter._get_services_object_from_container('92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04')
        mock_get_container_from_id.assert_called_once()
        mock_get_container_exposed_ports.assert_called_once()
        mock__get_container_labels_and_vars.assert_called_once()
        mock_get_local_node_name.assert_called_once()
        mock_get_local_node_address.assert_called_once()

        self.assertEqual(1, len(services))
        self.assertEqual('toto', services[0].name)
        self.assertEqual(1, len(services[0].nodes))
        self.assertEqual(3, len(services[0].tags))
        self.assertEqual(3000, services[0].port)

    @patch.object(SwarmAdapter, '_get_container_from_id', side_effect=[
        Container(
            id='92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04',
            attrs={
                'State': {'Status': 'created'},
                'Name': '/toto',
                'Config': {
                    'Labels': {
                        'com.docker.compose.service': 'project_toto'
                    }
                }
            }
        ),
        Container(
            id='92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04',
            attrs={
                'State': {'Status': 'running'},
                'Name': '/toto',
                'Config': {
                    'Labels': {
                        'com.docker.compose.service': 'project_toto'
                    }
                }
            }
        ),

    ])
    @patch.object(SwarmAdapter, '_get_container_exposed_ports', return_value=[{'internal_port': 80, 'external_port': 3000}])
    @patch.object(SwarmAdapter, '_get_container_labels_and_vars', return_value=[{"service_tags": 'http,https'}, ['service_name=toto']])
    @patch.object(SwarmAdapter, '_get_local_node_name', return_value='node1')
    @patch.object(SwarmAdapter, '_get_local_node_address', return_value='192.168.50.4')
    def test_get_services_object_from_container_not_running_first_time(self, mock_get_local_node_address, mock_get_local_node_name, mock__get_container_labels_and_vars, mock_get_container_exposed_ports, mock_get_container_from_id):
        services = self.swarm_adapter._get_services_object_from_container('92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04')
        self.assertEqual(2, mock_get_container_from_id.call_count)
        mock_get_container_exposed_ports.assert_called_once()
        mock__get_container_labels_and_vars.assert_called_once()
        mock_get_local_node_name.assert_called_once()
        mock_get_local_node_address.assert_called_once()

        self.assertEqual(1, len(services))
        self.assertEqual('toto', services[0].name)
        self.assertEqual(1, len(services[0].nodes))
        self.assertEqual(3, len(services[0].tags))
        self.assertEqual(3000, services[0].port)

    @patch.object(SwarmAdapter, '_get_container_from_id', return_value=Container(
        id='92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04',
        attrs={
            'State': {'Status': 'running'},
            'Name': '/toto',
            'Config': {
                'Labels': {
                    'com.docker.compose.service': 'project_toto'
                }
            }
        }
    ))
    @patch.object(SwarmAdapter, '_get_container_exposed_ports', return_value=[])
    @patch.object(SwarmAdapter, '_get_container_labels_and_vars', return_value=None)
    @patch.object(SwarmAdapter, '_get_local_node_name', return_value=None)
    @patch.object(SwarmAdapter, '_get_local_node_address', return_value=None)
    def test_get_services_object_from_container_not_exposed_port(self, mock_get_local_node_address, mock_get_local_node_name, mock__get_container_labels_and_vars, mock_get_container_exposed_ports, mock_get_container_from_id):
        services = self.swarm_adapter._get_services_object_from_container('92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04')
        mock_get_container_from_id.assert_called_once()
        mock_get_container_exposed_ports.assert_called_once()
        mock__get_container_labels_and_vars.assert_not_called()
        mock_get_local_node_name.assert_not_called()
        mock_get_local_node_address.assert_not_called()

        self.assertEqual(0, len(services))

    @patch.object(SwarmAdapter, '_list_nodes', return_value=[
        SwarmNode({'Status': {'State': 'ready', 'Addr': '192.168.50.4'}, 'Description': {'Hostname': 'node1'}}),
        SwarmNode({'Status': {'State': 'ready', 'Addr': '192.168.50.5'}, 'Description': {'Hostname': 'node2'}}),
        SwarmNode({'Status': {'State': 'ready', 'Addr': '192.168.50.6'}, 'Description': {'Hostname': 'node3'}}),
        SwarmNode({'Status': {'State': 'down', 'Addr': '192.168.50.7'}, 'Description': {'Hostname': 'node4'}})
    ])
    def test_get_nodes_for_service(self, mock_list_nodes):
        self.assertEqual(3, len(self.swarm_adapter._get_nodes_for_service(SwarmService(id='r1neuke2qg59ivhdblg4dvi7h'))))

    def test_get_service_exposed_ports(self):
        exposed_ports = self.swarm_adapter._get_service_exposed_ports(
            SwarmService(
                id='r1neuke2qg59ivhdblg4dvi7h',
                attrs={
                    'Endpoint': {
                        'Ports': [
                            {'PublishedPort': 3000, 'TargetPort': 80},
                            {'PublishedPort': 3001, 'TargetPort': 443}
                        ]
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

    def test_get_service_exposed_ports_empty(self):
        self.assertEqual(0, len(self.swarm_adapter._get_service_exposed_ports(SwarmService(id='r1neuke2qg59ivhdblg4dvi7h', attrs={'Endpoint': {}}))))

    @patch.object(SwarmAdapter, '_list_container', return_value=[
        Container(id='r1neuke2qg59ivhdblg4dvi7h.1', status='running', attrs={'Config': {'Labels': {'com.docker.swarm.service.id': 'r1neuke2qg59ivhdblg4dvi7h'}}}),
        Container(id='123456789', status='running', attrs={'Config': {'Labels': {}}}),
        Container(id='987654321', status='running', attrs={'Config': {'Labels': {}}}),
        Container(id='789123456', status='running', attrs={'Config': {'Labels': {}}})
    ])
    def test_get_containers(self, mock_list_containers):
        self.assertEqual(3, len(self.swarm_adapter._get_containers()))

    def test_get_container_exposed_ports(self):
        exposed_ports = self.swarm_adapter._get_container_exposed_ports(
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
        exposed_ports = self.swarm_adapter._get_container_exposed_ports(
            Container(
                id="123456789",
                attrs={"NetworkSettings": {"Ports": {}}}
            )
        )
        self.assertEqual(0, len(exposed_ports))

    def test__get_swarm_service_labels_and_vars(self):
        labels, envs = self.swarm_adapter._get_swarm_service_labels_and_vars(
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

    def test_get_container_labels_and_vars(self):
        labels, envs = self.swarm_adapter._get_container_labels_and_vars(
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

    def test_get_tags(self):
        self.assertEqual(
            ['http'],
            self.swarm_adapter._get_tags(labels={'service_tags': 'http', 'service_443_tags': 'https'}, envs=['service_80_tags=http'], internal_port=80)
        )

    def test_get_name_from_label_and_envs__labels_only(self):
        self.assertEqual(
            'hello',
            self.swarm_adapter._get_name_from_label_and_envs(labels={'service_name': 'hello'}, envs=[], internal_port=80)
        )

    def test_get_name_from_label_and_envs__envs_only(self):
        self.assertEqual(
            'hello',
            self.swarm_adapter._get_name_from_label_and_envs(labels={}, envs=['service_80_name=hello'], internal_port=80)
        )


