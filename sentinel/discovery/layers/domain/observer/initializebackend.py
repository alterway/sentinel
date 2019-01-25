from typing import Union
from zope.interface import implementer
from discovery.layers.domain import Factory
from discovery.layers.application.cqrs.command.discoverycmd import DiscoveryCommand
from ddd_domain_driven_design.application.observable.generalisation.interface.observer import ObserverInterface
from ddd_domain_driven_design.application.observable.generalisation.interface.observable import ObservableInterface


@implementer(ObserverInterface)
class InitializeBackend(object):

    def __init__(self, DiscoveryCommand: Union[DiscoveryCommand, None]):
        self.backend = Factory.backend(DiscoveryCommand)
        self.orchestrator = Factory.orchestrator(DiscoveryCommand)
        self.logger = Factory.logger(DiscoveryCommand)

    def update(self, subject: ObservableInterface):
        """
            Sync register services with effective running services

            :return:
        """
        registered_services = self.backend.get_services()
        running_services = self.orchestrator.get_services()

        for service in registered_services:
            self.logger.info("backend registered service: %s", service.name)

        for service in running_services:
            self.logger.info("Orchestrator registered service: %s", service.name)

        self.logger.info("INITIALIZE:::Deregister existing services if in backend...")
        for service in registered_services:
            self.backend.deregister_service(service)

        self.logger.info('INITIALIZE:::Register running services...')
        for service in running_services:
            self.backend.register_service(service)

        self.logger.info("Synchonisation is done")
