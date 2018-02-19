import unittest
from adapters.docker.container_adapter import ContainerAdapter
from adapters.docker.docker_adapter import DockerAdapter
from mock import patch
from utils.test_utilities import Container


class TestContainerAdapter(unittest.TestCase):

    def setUp(self):
        self.container_adapter = ContainerAdapter()

    @patch.object(DockerAdapter, 'get_container_from_id', return_value=Container(
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
    @patch.object(ContainerAdapter, '_get_container_exposed_ports', return_value=[{'internal_port': 80, 'external_port': 3000}, {'internal_port': 443, 'external_port': 30001}])
    @patch.object(ContainerAdapter, '_get_container_labels_and_vars', return_value=[{"service_80_tags": 'http'}, ['service_80_name=toto', 'not_register=1']])
    @patch.object(DockerAdapter, 'get_local_node_name', return_value='node1')
    @patch.object(DockerAdapter, 'get_local_node_address', return_value='192.168.50.4')
    def test_get_services_object(self, mock_get_local_node_address, mock_get_local_node_name, mock__get_container_labels_and_vars, mock_get_container_exposed_ports, mock_get_container_from_id):
        services = self.container_adapter._get_services_object('92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04')
        mock_get_container_from_id.assert_called_once()
        mock_get_container_exposed_ports.assert_called_once()
        self.assertEqual(1, mock__get_container_labels_and_vars.call_count)
        mock_get_local_node_name.assert_called_once()
        mock_get_local_node_address.assert_called_once()

        self.assertEqual(1, len(services))
        self.assertEqual('toto', services[0].name)
        self.assertEqual(1, len(services[0].nodes))
        self.assertEqual(2, len(services[0].tags))
        self.assertEqual(3000, services[0].port)

    @patch.object(DockerAdapter, 'get_container_from_id', side_effect=[
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
    @patch.object(ContainerAdapter, '_get_container_exposed_ports', return_value=[{'internal_port': 80, 'external_port': 3000}])
    @patch.object(ContainerAdapter, '_get_container_labels_and_vars', return_value=[{"service_tags": 'http,https'}, ['service_name=toto']])
    @patch.object(DockerAdapter, 'get_local_node_name', return_value='node1')
    @patch.object(DockerAdapter, 'get_local_node_address', return_value='192.168.50.4')
    def test_get_services_object_not_running_first_time(self, mock_get_local_node_address, mock_get_local_node_name, mock__get_container_labels_and_vars, mock_get_container_exposed_ports, mock_get_container_from_id):
        services = self.container_adapter._get_services_object('92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04')
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

    @patch.object(DockerAdapter, 'get_container_from_id', return_value=Container(
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
    @patch.object(ContainerAdapter, '_get_container_exposed_ports', return_value=[])
    @patch.object(ContainerAdapter, '_get_container_labels_and_vars', return_value=None)
    @patch.object(DockerAdapter, 'get_local_node_name', return_value=None)
    @patch.object(DockerAdapter, 'get_local_node_address', return_value=None)
    def test_get_services_object_not_exposed_port(self, mock_get_local_node_address, mock_get_local_node_name, mock__get_container_labels_and_vars, mock_get_container_exposed_ports, mock_get_container_from_id):
        services = self.container_adapter._get_services_object('92aa516a0cef6dbba682011c3ecc2f57036852f0658e51ba5f1f364419b95d04')
        mock_get_container_from_id.assert_called_once()
        mock_get_container_exposed_ports.assert_called_once()
        mock__get_container_labels_and_vars.assert_not_called()
        mock_get_local_node_name.assert_not_called()
        mock_get_local_node_address.assert_not_called()

        self.assertEqual(0, len(services))

    @patch.object(DockerAdapter, 'list_container', return_value=[
        Container(id='r1neuke2qg59ivhdblg4dvi7h.1', status='running', attrs={'Config': {'Labels': {'com.docker.swarm.service.id': 'r1neuke2qg59ivhdblg4dvi7h'}}}),
        Container(id='123456789', status='running', attrs={'Config': {'Labels': {}}}),
        Container(id='987654321', status='running', attrs={'Config': {'Labels': {}}}),
        Container(id='789123456', status='running', attrs={'Config': {'Labels': {}}})
    ])
    @patch.object(DockerAdapter, 'get_container_from_id', side_effect=[
        Container(id='123456789', status='running', attrs={'Name': 'c1', 'State': {'Status': 'running'}, 'Config': {'Labels': {}}, "NetworkSettings": {"Ports": {"80/tcp": [{"HostPort": '3000'}]}}}),
        Container(id='987654321', status='running', attrs={'Name': 'c2', 'State': {'Status': 'running'}, 'Config': {'Labels': {}}, "NetworkSettings": {"Ports": {"80/tcp": [{"HostPort": '3001'}]}}}),
        Container(id='789123456', status='running', attrs={'Name': 'c3', 'State': {'Status': 'running'}, 'Config': {'Labels': {}}, "NetworkSettings": {"Ports": {"80/tcp": [{"HostPort": '3002'}]}}})
    ])
    @patch.object(DockerAdapter, 'get_local_node_name', return_value='node1')
    @patch.object(DockerAdapter, 'get_local_node_address', return_value='192.168.50.4')
    def test_get_services(self, mock_get_node_address, mock_get_node_name, mock_get_container_from_id, mock_list_containers):
        self.assertEqual(3, len(self.container_adapter.get_services()))
        mock_list_containers.assert_called_once()
        self.assertEqual(3, mock_get_container_from_id.call_count)
        self.assertEqual(3, mock_get_node_name.call_count)
        self.assertEqual(3, mock_get_node_address.call_count)

    def test_get_container_exposed_ports(self):
        exposed_ports = self.container_adapter._get_container_exposed_ports(
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
        exposed_ports = self.container_adapter._get_container_exposed_ports(
            Container(
                id="123456789",
                attrs={"NetworkSettings": {"Ports": {}}}
            )
        )
        self.assertEqual(0, len(exposed_ports))

    def test_get_container_labels_and_vars(self):
        labels, envs = self.container_adapter._get_container_labels_and_vars(
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
