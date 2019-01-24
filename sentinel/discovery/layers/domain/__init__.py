import os
import importlib
import logging
from discovery.layers.application.cqrs.command.discoverycmd import DiscoveryCommand
from discovery.layers.domain.orchestrator.generalisation.interface.orchestrator import OrchestratorInterface
from discovery.layers.domain.backend.generalisation.interface.backend import BackendInterface


class Factory:
    _instances = {}

    @staticmethod
    def logger(DiscoveryCommand: DiscoveryCommand):
        """Return the sentinel logger"""
        key_class = 'logger'
        if key_class not in Factory._instances:
            logger = logging.getLogger('STDOUT')
            if os.environ.get('TESTING_MODE'):
                logger.setLevel(DiscoveryCommand.level)
            Factory._instances[key_class] = logger

        return Factory._instances[key_class]

    @staticmethod
    def service_container(DiscoveryCommand: DiscoveryCommand):
        """Return adapter to get container services"""
        key_class = 'service_container'
        if key_class not in Factory._instances:
            from discovery.layers.domain.service.containerservice import ContainerService
            Factory._instances[key_class] = ContainerService(Factory.docker_adapter(), DiscoveryCommand.address,
                                                             Factory.logger(DiscoveryCommand))

        return Factory._instances[key_class]

    @staticmethod
    def service_swarm(DiscoveryCommand: DiscoveryCommand):
        """Return adapter to get swarm services"""
        key_class = 'service_swarm'
        if key_class not in Factory._instances:
            from discovery.layers.domain.service.swarmservice import SwarmService
            Factory._instances[key_class] = SwarmService(Factory.swarm_adapter(), Factory.logger(DiscoveryCommand))

        return Factory._instances[key_class]

    @staticmethod
    def backend(DiscoveryCommand: DiscoveryCommand) -> BackendInterface:
        """Return adapter for the desired backend"""
        key_class = 'backend'
        if key_class not in Factory._instances:
            from discovery.layers.infrastructure.api.consul import ApiConsulFactory

            backend_class = getattr(
                importlib.import_module('discovery.layers.domain.backend.%s' % DiscoveryCommand.backend),
                DiscoveryCommand.backend.capitalize()
            )
            Factory._instances[key_class] = backend_class(
                DiscoveryCommand.address,
                Factory.logger(DiscoveryCommand),
                Factory.adapter(DiscoveryCommand),
                ApiConsulFactory()
            )

        return Factory._instances[key_class]

    @staticmethod
    def orchestrator(DiscoveryCommand: DiscoveryCommand) -> OrchestratorInterface:
        """Return adapter for the desired orchestrator"""
        key_class = 'orchestrator'
        if key_class not in Factory._instances:
            orchestrator_class = getattr(
                importlib.import_module('discovery.layers.domain.orchestrator.%s' % DiscoveryCommand.orchestrator),
                DiscoveryCommand.orchestrator.capitalize()
            )
            Factory._instances[key_class] = orchestrator_class(
                Factory.backend(DiscoveryCommand),
                Factory.service_swarm(DiscoveryCommand),
                Factory.service_container(DiscoveryCommand),
                Factory.logger(DiscoveryCommand.level)
            )

        return Factory._instances[key_class]

    @staticmethod
    def adapter(DiscoveryCommand: DiscoveryCommand):
        key_class = 'adapter'
        if key_class not in Factory._instances:
            if DiscoveryCommand.orchestrator == 'kube':
                Factory._instances[key_class] = Factory.kube_adapter()
            elif DiscoveryCommand.orchestrator == 'swarm':
                Factory._instances[key_class] = Factory.swarm_adapter()
            else:
                Factory._instances[key_class] = Factory.docker_adapter()

        return Factory._instances[key_class]

    @staticmethod
    def docker_adapter():
        """Return adapter for the docker version"""
        key_class = 'docker_adapter'
        if key_class not in Factory._instances:
            from discovery.layers.domain.adapter.docker import DockerAdapter
            docker_adapter = DockerAdapter()

            if os.environ.get('TESTING_MODE'):
                docker_version = os.environ.get('TESTED_DOCKER_VERSION')
            else:
                docker_version = docker_adapter.get_version()

            try:
                Factory._instances[key_class] = getattr(
                    importlib.import_module('discovery.layers.domain.adapters.version_%s' % docker_version),
                    'DockerVersionAdapter'
                )
            except ImportError:
                Factory._instances[key_class] = docker_adapter

        return Factory._instances[key_class]

    @staticmethod
    def swarm_adapter():
        """Return adapter for the docker swarm version"""
        key_class = 'swarm_adapter'
        if key_class not in Factory._instances:
            from discovery.layers.domain.adapter.swarm import SwarmAdapter
            swarm_adapter = SwarmAdapter()

            if os.environ.get('TESTING_MODE'):
                docker_version = os.environ.get('TESTED_DOCKER_VERSION')
            else:
                docker_version = swarm_adapter.get_version()

            try:
                Factory._instances[key_class] = getattr(
                    importlib.import_module('discovery.layers.domain.adapters.version_%s' % docker_version),
                    'SwarmVersionAdapter'
                )
            except ImportError:
                Factory._instances[key_class] = swarm_adapter

        return Factory._instances[key_class]

    @staticmethod
    def kube_adapter():
        return {}
