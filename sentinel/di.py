import os
import importlib


def backend_adapter():
    backend = os.environ.get("BACKEND") if os.environ.get("BACKEND") else "consul"
    backend_class = getattr(
        importlib.import_module('backends.%s' % backend),
        backend.capitalize()
    )
    return backend_class()


def orchestrator_adapter():
    orchestrator = os.environ.get("ORCHESTRATOR") if os.environ.get("ORCHESTRATOR") else "swarm"
    return getattr(
        importlib.import_module('orchestrators.%s' % orchestrator),
        orchestrator.capitalize()
    )


def docker_adapter():
    from docker_adapters.docker_adapter import DockerAdapter

    if os.environ.get('ORCHESTRATOR') == 'swarm':
        return swarm_adapter()

    if os.environ.get('TESTING_MODE'):
        docker_version = os.environ.get('TESTED_DOCKER_VERSION')
    else:
        docker_version = DockerAdapter.get_version()

    try:
        return getattr(
            importlib.import_module('docker_adapters.docker_%s' % docker_version),
            'DockerVersionAdapter'
        )
    except Exception:
        return DockerAdapter


def swarm_adapter():
    from docker_adapters.swarm_adapter import SwarmAdapter

    if os.environ.get('TESTING_MODE'):
        docker_version = os.environ.get('TESTED_DOCKER_VERSION')
    else:
        docker_version = SwarmAdapter.get_version()

    try:
        return getattr(
            importlib.import_module('docker_adapters.swarm_%s' % docker_version),
            'SwarmVersionAdapter'
        )
    except Exception:
        return SwarmAdapter


def container_adapter():
    from service.container import Container
    return Container


def swarmservice_adapter():
    from service.swarmservice import SwarmService
    return SwarmService


def logger():
    import logging
    logger = logging.getLogger('STDOUT')
    if os.environ.get('TESTING_MODE'):
        logger.setLevel('CRITICAL')

    return logger


def not_implemented():
    from exceptions import not_implemented
    return not_implemented


DEPENDENCIES = {
    "backend_adapter": backend_adapter,
    "orchestrator_adapter": orchestrator_adapter,
    "docker_adapter": docker_adapter,
    "swarm_adapter": swarm_adapter,
    "container_adapter": container_adapter,
    "swarmservice_adapter": swarmservice_adapter,
    "not_implemented": not_implemented,
    "logger": logger
}
