from utils.dependencies_injection import inject_param
from utils.logger import set_logging


@inject_param('backend_adapter')
@inject_param('orchestrator_adapter')
@inject_param('logger')
def sync(backend_adapter=None, orchestrator_adapter=None, logger=None):
    registered_services = backend_adapter.get_services()
    running_services = orchestrator_adapter.get_services()

    # Register existant services if not in backend
    logger.info("Register existant services if not in backend...")
    registered_services_names = [service.name for service in registered_services]
    for service in running_services:
        if service.name not in registered_services_names:
            backend_adapter.register_service(service)

    # Deregister services in backend if not running
    logger.info('Deregister in backend not running services...')
    running_services_names = [service.name for service in running_services]
    for service in registered_services:
        if service.name not in running_services_names:
            backend_adapter.deregister_service(service)

    logger.info("Synchonisation is done")


@inject_param("orchestrator_adapter")
@inject_param("logger")
def listen_events(orchestrator_adapter=None, logger=None):
    orchestrator_adapter.listen_events()


def main():
    set_logging()
    sync()
    listen_events()
