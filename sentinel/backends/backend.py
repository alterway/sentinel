from zope.interface import Interface, Attribute


class Backend(Interface):  # pylint: disable-msg=inherit-non-class
    """Interface to create backend adapters"""

    address = Attribute("""Address to get backend""")

    def get_services(docker_adapter=None, logger=None):
        """Get service in backend"""

    def register_service(service, logger=None):
        """Register a service in backend"""

    def deregister_node(service, logger=None):
        """Deregister a service in backend"""
