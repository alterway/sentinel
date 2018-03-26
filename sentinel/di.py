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
    from services_adapters.docker_adapter import DockerAdapter
    return DockerAdapter()


def container_adapter():
    from services_adapters.container import Container
    return Container


def swarmservice_adapter():
    from services_adapters.swarmservice import SwarmService
    return SwarmService


def logger():
    import logging
    return logging.getLogger('STDOUT')


def not_implemented():
    from exceptions import not_implemented
    return not_implemented


DEPENDENCIES = {
    "backend_adapter": backend_adapter,
    "orchestrator_adapter": orchestrator_adapter,
    "docker_adapter": docker_adapter,
    "container_adapter": container_adapter,
    "swarmservice_adapter": swarmservice_adapter,
    "not_implemented": not_implemented,
    "logger": logger
}
