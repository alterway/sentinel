class NotImplemented(Exception):
    def __init__(self, message):
        self.message = message


class RegisterFailed(Exception):
    def __init__(self, message):
        self.message = message


class BackendAdapterNotKnown(Exception):
    def __init__(self, backend):
        self.message = 'Backend adpater doesn\'t exists : %s' % backend


class OrchestratorAdapterNotKnown(Exception):
    def __init__(self, orchestrator):
        self.message = 'Orchestrator adapter doesn\'t exists : %s' % orchestrator
