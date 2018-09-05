"""Sentinel Exceptions"""


class SentinelBaseError(Exception):
    """
    SentinelBaseError Exception
    All exceptions define in sentinel module need to inherit this Error class
    """
    def __init__(self, message):
        self.message = message
        super().__init__()


class BackendAdapterNotKnown(SentinelBaseError):
    """Raise when specified backend is not implemented"""
    def __init__(self, backend):
        super().__init__('Backend adpater doesn\'t exists : %s' % backend)


class OrchestratorAdapterNotKnown(SentinelBaseError):
    """Raise when specified orchestrator is not implemented"""
    def __init__(self, orchestrator):
        super().__init__('Orchestrator adapter doesn\'t exists : %s' % orchestrator)


class InvalidIPAddress(SentinelBaseError):
    """Raise when ip address found for service is not valid"""
    def __init__(self, address):
        super().__init__('IP %s is not a valid ip address' % address)
