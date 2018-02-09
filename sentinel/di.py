import os


def backend_adapter():
    if os.environ.get('BACKEND') == "consul":
        from adapters.backends.consul import ConsulAdapter
        return ConsulAdapter()


def orchestrator_adapter():
    if os.environ.get('ORCHESTRATOR') == "swarm":
        from adapters.orchestrators.swarm import SwarmAdapter
        return SwarmAdapter()


def docker_adapter():
    from adapters.docker.docker_adapter import DockerAdapter
    return DockerAdapter()


def container_adapter():
    from adapters.docker.container_adapter import ContainerAdapter
    return ContainerAdapter()


def swarmservice_adapter():
    from adapters.docker.swarmservice_adapter import SwarmServiceAdapter
    return SwarmServiceAdapter()


def logger():
    import logging
    return logging.getLogger('STDOUT')


DEPENDENCIES = {
    "backend_adapter": backend_adapter,
    "orchestrator_adapter": orchestrator_adapter,
    "docker_adapter": docker_adapter,
    "container_adapter": container_adapter,
    "swarmservice_adapter": swarmservice_adapter,
    "logger": logger
}
