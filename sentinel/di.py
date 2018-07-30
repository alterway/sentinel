"""Define dependencies injections"""
import os
import importlib


def backend_adapter():
    """Return adapter for the desired backend"""
    backend = os.environ.get("BACKEND") if os.environ.get("BACKEND") else "consul"
    backend_class = getattr(
        importlib.import_module('backends.%s' % backend),
        backend.capitalize()
    )
    return backend_class()


def orchestrator_adapter():
    """Return adapter for the desired orchestrator"""
    orchestrator = os.environ.get("ORCHESTRATOR") if os.environ.get("ORCHESTRATOR") else "swarm"
    return getattr(
        importlib.import_module('orchestrators.%s' % orchestrator),
        orchestrator.capitalize()
    )


def docker_adapter():
    """Return adapter for the docker version"""
    from docker_adapters.base import DockerAdapter

    if os.environ.get('ORCHESTRATOR') == 'swarm':
        return swarm_adapter()

    if os.environ.get('TESTING_MODE'):
        docker_version = os.environ.get('TESTED_DOCKER_VERSION')
    else:
        docker_version = DockerAdapter.get_version()

    try:
        return getattr(
            importlib.import_module('docker_adapters.version_%s' % docker_version),
            'DockerVersionAdapter'
        )
    except ImportError:
        return DockerAdapter


def swarm_adapter():
    """Return adapter for the docker swarm version"""
    from docker_adapters.base import SwarmAdapter

    if os.environ.get('TESTING_MODE'):
        docker_version = os.environ.get('TESTED_DOCKER_VERSION')
    else:
        docker_version = SwarmAdapter.get_version()

    try:
        return getattr(
            importlib.import_module('docker_adapters.version_%s' % docker_version),
            'SwarmVersionAdapter'
        )
    except ImportError:
        return SwarmAdapter


def container_adapter():
    """Return adapter to get container services"""
    from service.container import Container
    return Container


def swarmservice_adapter():
    """Return adapter to get swarm services"""
    from service.swarmservice import SwarmService
    return SwarmService


def get_logger():  # pylint: disable-msg=redefined-outer-name
    """Return the sentinel logger"""
    import logging
    logger = logging.getLogger('STDOUT')
    if os.environ.get('TESTING_MODE'):
        logger.setLevel('CRITICAL')

    return logger


DEPENDENCIES = {
    "backend_adapter": backend_adapter,
    "orchestrator_adapter": orchestrator_adapter,
    "docker_adapter": docker_adapter,
    "swarm_adapter": swarm_adapter,
    "container_adapter": container_adapter,
    "swarmservice_adapter": swarmservice_adapter,
    "logger": get_logger
}
