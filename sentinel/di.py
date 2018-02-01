import os
#from exceptions import OrchestratorAdapterNotKnown, BackendAdapterNotKnown


def backend_adapter():
    if os.environ.get('BACKEND') == "consul":
        from adapters.backends.consul import ConsulAdapter
        return ConsulAdapter()

    raise BackendAdapterNotKnown(os.environ.get('BACKEND'))


def orchestrator_adapter():
    if os.environ.get('ORCHESTRATOR') == "swarm":
        from adapters.orchestrators.swarm import SwarmAdapter
        return SwarmAdapter()

    raise OrchestratorAdapterNotKnown(os.environ.get('ORCHESTRATOR'))


def logger():
    import logging
    return logging.getLogger('STDOUT')


DEPENDENCIES = {
    "backend_adapter": backend_adapter,
    "orchestrator_adapter": orchestrator_adapter,
    "logger": logger
}
