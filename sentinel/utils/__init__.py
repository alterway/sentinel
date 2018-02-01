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
    logger = logging.getLogger(__name__)
    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    logger.addHandler(out_hdlr)
    logger.setLevel(logging.INFO if os.environ.get('DEBUG') is None else logging.DEBUG)

    return logger


DEPENDENCIES = {
    "backend_adapter": backend_adapter,
    "orchestrator_adapter": orchestrator_adapter,
    "logger": logger
}
