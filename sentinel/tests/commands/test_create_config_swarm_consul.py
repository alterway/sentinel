from unittest import TestCase
from commands.create_config import ConfigManager
import os


class CreateConfigSwarmConsulTest(TestCase):

    def setUp(self):
        self.manager = ConfigManager
        self.kwargs = {
            '--swarm-managers-hostname': 'node1,node2,node3',
            '--swarm-workers-hostname': 'node4'
        }
        self.maxDiff = None
        self.current_path = os.path.dirname(os.path.abspath(__file__))

    def test_swarm_consul_gen_config_success_swarmservices(self):
        self.manager.swarm_consul_gen_config(**self.kwargs)
        self.assertEqual(True, os.path.isfile('/config/docker-compose.yml'))

        with open('%s/swarm_consul_swarmservices_config_expected.yml' % self.current_path, 'r') as f:
            expected_config = f.read()

        with open("/config/docker-compose.yml", 'r') as f:
            rendered_config = f.read()

        self.assertEqual(expected_config, rendered_config)
        os.remove("/config/docker-compose.yml")

    def test_swarm_consul_gen_config_success_compose(self):
        self.kwargs['--deployment-type'] = 'compose'
        self.kwargs['--bootstrap-address'] = "192.168.50.4"
        self.manager.swarm_consul_gen_config(**self.kwargs)
        self.assertEqual(True, os.path.isfile('/config/docker-compose-node1.yml'))
        self.assertEqual(True, os.path.isfile('/config/docker-compose-node2.yml'))
        self.assertEqual(True, os.path.isfile('/config/docker-compose-node3.yml'))
        self.assertEqual(True, os.path.isfile('/config/docker-compose-node4.yml'))

        nodes = self.kwargs['--swarm-managers-hostname'].split(',')
        nodes.extend(self.kwargs['--swarm-workers-hostname'].split(','))
        for node in nodes:
            with open('%s/swarm_consul_compose_%s_expected.yml' % (self.current_path, node), 'r') as f:
                expected_config = f.read()

            with open('/config/docker-compose-%s.yml' % node, 'r') as f:
                rendered_config = f.read()

            self.assertEqual(
                expected_config,
                rendered_config,
                "Expected config files %s is different of the rendered config files %s" % (
                    'swarm_consul_compose_%s_expected.yml' % node, '/config/docker-compose-%s.yml' % node
                )
            )

            os.remove('/config/docker-compose-%s.yml' % node)

    def test_swarm_consul_gen_config_failed_no_managers(self):
        del self.kwargs['--swarm-managers-hostname']
        with self.assertRaises(SystemExit):
            with self.assertLogs(level='ERROR') as log:
                self.manager.swarm_consul_gen_config(**self.kwargs)
                self.assertEqual(
                    True,
                    'Create config failed : swarm managers hostname need to be specified with'
                    ' parameter "--swarm-managers-hostname"' in log.output
                )

    def test_swarm_consul_gen_config_failed_no_bootstrap_address(self):
        self.kwargs['--deployment-type'] = 'compose'
        with self.assertRaises(SystemExit):
            with self.assertLogs(level='ERROR') as log:
                self.manager.swarm_consul_gen_config(**self.kwargs)
                self.assertEqual(
                    True,
                    "Can't generate docker-compose files if not bootstrap address given" in log.output
                )

    def test_create_config_success(self):
        self.kwargs['--orchestrator'] = 'swarm'
        self.kwargs['--backend'] = 'consul'
        self.manager.create_config(**self.kwargs)
        self.assertEqual(True, os.path.isfile('/config/docker-compose.yml'))

        with open('%s/swarm_consul_swarmservices_config_expected.yml' % self.current_path, 'r') as f:
            expected_config = f.read()

        with open("/config/docker-compose.yml", 'r') as f:
            rendered_config = f.read()

        self.assertEqual(expected_config, rendered_config)
        os.remove("/config/docker-compose.yml")

    def test_create_config_failed_no_orchestrator(self):
        with self.assertRaises(SystemExit):
            with self.assertLogs(level='ERROR') as log:
                self.manager.create_config(**self.kwargs)
                self.assertEqual(
                    True,
                    "Orchestrator and backend need to be specified" in log.output
                )

    def test_create_config_failed_no_method(self):
        self.kwargs['--orchestrator'] = 'badorchestrator'
        with self.assertRaises(SystemExit):
            with self.assertLogs(level='ERROR') as log:
                self.manager.create_config(**self.kwargs)
                self.assertEqual(
                    True,
                    "No method to configure orchestrator 'badorchestrator' with backend 'consul'" in log.output
                )
