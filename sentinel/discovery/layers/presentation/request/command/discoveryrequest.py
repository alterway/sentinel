from zope.interface import implementer
from ddd_domain_driven_design.presentation.request.generalisation.interface.request import RequestInterface


@implementer(RequestInterface)
class DiscoveryRequest(object):
    """Adapter to create Command"""

    def __init__(self, args):
        self.args = args

    def get_request_parameters(self):
        """Create json string data from args"""

        return '{"backend": "%s", "orchestrator": "%s", "address": "%s", "level": "%s"}' % (self.args.backend,
                                                                                            self.args.orchestrator,
                                                                                            self.args.target,
                                                                                            self.args.log_level.upper())
