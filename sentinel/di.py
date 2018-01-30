import os
from exceptions import OrchestratorAdapterNotKnown, BackendAdapterNotKnown


def backend_adpater(self):
    if os.environ.get('BACKEND') == "consul":
        from adapters.backend.consul import ConsulAdapter
        return ConsulAdapter()

    raise BackendAdapterNotKnown(os.environ.get('BACKEND'))


def orchestrator_adapter(self):
    if os.environ.get('ORCHESTRATOR') == "swarm":
        from adapters.orchestrator.swarm import SwarmAdapter
        return SwarmAdapter()

    raise OrchestratorAdapterNotKnown(os.environ.get('ORCHESTRATOR'))


DEPENDENCIES = {
    "backend_adapter": backend_adapter,
    "orchestrator_adapter": orchestrator_adapter
}
