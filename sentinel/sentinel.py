from utils.dependencies_injection import inject_param
from utils.logger import set_logging
import docker
from datetime import datetime


@inject_param('backend_adapter')
@inject_param('orchestrator_adapter')
@inject_param('logger')
def process_event(event, backend_adapter=None, orchestrator_adapter=None, logger=None):
    if event['Action'] == 'create':
        logger.debug("Get event create : %s" % event)
        service = orchestrator_adapter.get_service(event)
        if service is not None:
            backend_adapter.register_service(service)

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

    logger.info("Synchonisation is done")


@inject_param("logger")
def listen_events(logger=None):
    logger.info("Listen docker events...")
    client = docker.DockerClient(base_url='unix://var/run/docker.sock', version='auto')
    for event in client.events(since=datetime.utcnow(), decode=True):
        process_event(event)


if __name__ == "__main__":
    set_logging()
    sync()
    listen_events()


