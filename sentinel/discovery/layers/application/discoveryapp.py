from typing import Union
from discovery.layers.application.cqrs.command.discoverycmd import DiscoveryCommand
from ddd_domain_driven_design.application.observable.observable import Observable
from discovery.layers.domain.observer.initializebackend import InitializeBackend
from discovery.layers.domain.observer.listenevents import ListenEvents


class DiscoveryApp(object):

    def __init__(self, DiscoveryCommand: Union[DiscoveryCommand, None]):
        self.command = DiscoveryCommand

    def run(self):
        """
            running discovery application

            :return:
        """
        observable = Observable()
        observable.attach(InitializeBackend(self.command))
        observable.attach(ListenEvents(self.command))
        observable.process(None)


