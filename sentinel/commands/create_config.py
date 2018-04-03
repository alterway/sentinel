from utils.dependencies_injection import inject_param
from jinja2 import Environment, PackageLoader, select_autoescape
import sys
import os


class SwarmNodesConfig():
    @inject_param('logger')
    def __init__(
        self, managers_hostname, workers_hostname=[], bootstrap_address=None,
        deployment_type='swarmservices', domain='docker.local', logger=None
    ):
        deployment_type_choices = ["swarmservices", "compose"]
        if deployment_type not in deployment_type_choices:
            logger.error("%s is not a valid deployment_type : %s" % (
                deployment_type, deployment_type_choices
            ))
            sys.exit(1)

        self.managers_hostname = managers_hostname
        self.workers_hostname = workers_hostname
        self.deployment_type = deployment_type
        self.domain = domain
        self.bootstrap_address = bootstrap_address

    def generate(self):
        getattr(self, '_gen_config_%s' % self.deployment_type)()

    def _gen_config_swarmservices(self):
        config = self._render(
            BOOTSTRAP_HOSTNAME=self.managers_hostname[0],
            MANAGERS_HOSTNAME=self.managers_hostname,
            WORKERS_HOSTNAME=self.workers_hostname,
            DOMAIN=self.domain
        )

        self._write(config=config, filename='docker-compose.yml')

    @inject_param('logger')
    def _gen_config_compose(self, logger=None):
        if not self.bootstrap_address:
            logger.error("Can't generate docker-compose files if not bootstrap address given")
            sys.exit(1)

        nodes_config = {}

        # Render docker-compose for all managers
        for index, manager in enumerate(self.managers_hostname):
            nodes_config[manager] = self._render(
                HOSTNAME=manager,
                DOMAIN=self.domain,
                BOOTSTRAP_ADDRESS=self.bootstrap_address,
                IS_BOOTSTRAP=(index == 0),
                IS_SERVER=True
            )

        # Render docker-compose for all workers
        for worker in self.workers_hostname:
            nodes_config[worker] = self._render(
                HOSTNAME=worker,
                DOMAIN=self.domain,
                BOOTSTRAP_ADDRESS=self.bootstrap_address,
                IS_BOOTSTRAP=False,
                IS_SERVER=False
            )

        # Write all docker-compose files
        for node in nodes_config.keys():
            self._write(
                config=nodes_config[node],
                filename='docker-compose-%s.yml' % node
            )

    def _render(self, **kwargs):
        env = Environment(
            loader=PackageLoader('commands', 'templates'),
            autoescape=select_autoescape(['yml'])
        )
        template = env.get_template(
            'swarm-consul-%s.yml.j2' % self.deployment_type
        )
        return template.render(kwargs)

    @staticmethod
    def _write(config, filename):
        if not os.path.exists('/config'):
            os.mkdir('/config')

        with open('/config/%s' % filename, 'w') as f:
            f.write(config)


class ConfigManager():

    @classmethod
    @inject_param('logger')
    def create_config(cls, logger=None, **kwargs):
        orchestrator = None
        backend = "consul"

        if '--orchestrator' in kwargs:
            orchestrator = kwargs['--orchestrator']

        if '--backend' in kwargs:
            backend = kwargs['--backend']

        if not orchestrator or not backend:
            logger.error('Orchestrator and backend need to be specified')
            sys.exit(1)

        try:
            getattr(cls, '%s_%s_gen_config' % (orchestrator, backend))(**kwargs)
        except AttributeError:
            logger.error(
                "No method to configure orchestrator '%s' with backend '%s'" % (
                    orchestrator, backend
                )
            )
            sys.exit(1)

    @staticmethod
    @inject_param('logger')
    def swarm_consul_gen_config(logger=None, **kwargs):
        if '--swarm-managers-hostname' in kwargs:
            swarm_config = SwarmNodesConfig(
                managers_hostname=kwargs['--swarm-managers-hostname'],
                workers_hostname=kwargs['--swarm-workers-hostname'] if '--swarm-workers-hostname' in kwargs else [],
                bootstrap_address=kwargs['--bootstrap-address'] if '--bootstrap-address' in kwargs else None,
                domain=kwargs['--domain'] if '--domain' in kwargs else 'docker.local',
                deployment_type=kwargs['--deployment-type'] if '--deployment-type' in kwargs else 'swarmservices'
            )
        else:
            logger.error(
                'Create config failed : swarm managers hostname need to be specified with'
                ' parameter "--swarm-managers-hostname"')
            sys.exit(1)

        swarm_config.generate()
