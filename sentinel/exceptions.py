class NotImplementedException(NotImplementedError):
    def __init__(self, method, class_name):
        self.message = "Methode %s is not implemented for %s" % (
            method, class_name
        )


class BackendAdapterNotKnown(Exception):
    def __init__(self, backend):
        self.message = 'Backend adpater doesn\'t exists : %s' % backend


class OrchestratorAdapterNotKnown(Exception):
    def __init__(self, orchestrator):
        self.message = 'Orchestrator adapter doesn\'t exists : %s' % orchestrator


class InvalidIPAddress(Exception):
    def __init__(self, address):
        self.message = 'IP %s is not a valid ip address' % address


def not_implemented(class_name):
    import inspect
    raise NotImplementedException(inspect.stack()[1][3], class_name)
