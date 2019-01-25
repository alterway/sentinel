from typing import Union
from zope.interface import implementer
from discovery.layers.domain import Factory
from discovery.layers.application.cqrs.command.discoverycmd import DiscoveryCommand
from ddd_domain_driven_design.application.observable.generalisation.interface.observer import ObserverInterface
from ddd_domain_driven_design.application.observable.generalisation.interface.observable import ObservableInterface


@implementer(ObserverInterface)
class ListenEvents(object):

    def __init__(self, DiscoveryCommand: Union[DiscoveryCommand, None]):
        self.orchestrator = Factory.orchestrator(DiscoveryCommand)

    def update(self, subject: ObservableInterface):
        """
            Start listen docker events
            :return:
        """
        self.orchestrator.listen_events()
