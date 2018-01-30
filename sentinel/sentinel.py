from utils.dependencies_injection import inject_param


@inject_param('backend_adapter')
@inject_param('orchestrator_adapter')
def sync(backend_adapter=None, orchestrator_adapter=None):
    pass
