"""Exceptions"""
from ddd_domain_driven_design.infrastructure.generalisation.exceptions import BaseError


class BackendAdapterNotKnown(BaseError):
    """Raise when specified backend is not implemented"""
    def __init__(self, backend):
        super().__init__('Backend adpater doesn\'t exists : %s' % backend)


class OrchestratorAdapterNotKnown(BaseError):
    """Raise when specified orchestrator is not implemented"""
    def __init__(self, orchestrator):
        super().__init__('Orchestrator adapter doesn\'t exists : %s' % orchestrator)


class InvalidIPAddress(BaseError):
    """Raise when ip address found for service is not valid"""
    def __init__(self, address):
        super().__init__('IP %s is not a valid ip address' % address)
