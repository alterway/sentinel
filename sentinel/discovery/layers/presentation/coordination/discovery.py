from ddd_domain_driven_design.presentation.adapter.commandadapter import CommandAdapter
from discovery.layers.presentation.request.command.discoveryrequest import DiscoveryRequest
from discovery.layers.application.discoveryapp import DiscoveryApp
from discovery.layers.application.cqrs.command.discoverycmd import DiscoveryCommand

DEFAULT_LOG_LEVEL = 'info'


class Discovery:
    name = "discovery"

    def options(self, subparsers):
        parser = subparsers.add_parser('discovery', help='Service Discovery help')
        parser.set_defaults(func=self.coordinate)

        parser.add_argument('-b', '--backend', type=str, default='consul',
                            help='To configure the backend to register services, only consul for now.')
        parser.add_argument('-o', '--orchestrator', type=str, default='swarm',
                            help='To configure the cluster docker orchestrator, only swarm for now')
        parser.add_argument('-t', '--target', type=str, default='127.0.0.1:8500',
                            help='The address to get consul catalog. You need to have an consul agent on all nodes '
                                 'because the address agent is the node cluster address to register services.')

    @staticmethod
    def coordinate(args, logger=None):
        """
        Coordinate the orchestration of services in the backend
        :param args:
        :param logger:
        :return:
        """
        adapter = CommandAdapter(DiscoveryCommand)
        command = adapter.create_command_from_request(DiscoveryRequest(args))

        application = DiscoveryApp(command)

        application.run()
