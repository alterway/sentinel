"""Main module to listen events, get services and register them in backend"""
import importlib
import sys
from dependencies_injection.inject_param import inject_param

from utils.logger import set_logging


@inject_param('backend_adapter')
@inject_param('orchestrator_adapter')
@inject_param('logger')
def sync(backend_adapter=None, orchestrator_adapter=None, logger=None):
    '''Sync register services with effective running services'''
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
def listen_events(orchestrator_adapter=None):
    '''Start listen docker events'''
    orchestrator_adapter.listen_events()


def _get_kwargs_from_argv(argv):
    kwargs = {}
    for index, arg in enumerate(argv):
        if index > 1:
            if '--h' in arg:
                kwargs['--help'] = True
                break

            argument_value = arg.split("=")
            if len(argument_value) == 2:
                kwargs[argument_value[0]] = argument_value[1]

    return kwargs


def main():
    """
    Main entry for sentinel program
    Sync registred services with effective running services
    and start listen docker events for services updates
    """
    if len(sys.argv) == 1:
        set_logging()
        sync()
        listen_events()
    else:
        kwargs = _get_kwargs_from_argv(sys.argv)
        getattr(
            importlib.import_module('commands.%s' % sys.argv[1]),
            'run'
        )(**kwargs)
