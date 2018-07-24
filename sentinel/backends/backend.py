# pylint: skip-file
"""Define backend interface for backend adapters"""
from zope.interface import Interface, Attribute


class Backend(Interface):
    """Interface to create backend adapters"""

    address = Attribute("""Address to get backend""")

    def get_services(docker_adapter=None, logger=None): # noqa
        """Get service in backend"""

    def register_service(service, logger=None): # noqa
        """Register a service in backend"""

    def deregister_node(service, logger=None): # noqa
        """Deregister a service in backend"""
