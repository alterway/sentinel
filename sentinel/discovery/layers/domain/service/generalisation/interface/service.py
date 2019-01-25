# pylint: skip-file
"""Implement Service interface to to manage docker service"""
from zope.interface import Interface


class ServiceInterface(Interface):
    """Interface to manage docker service"""

    def get_services():
        """Create services object from docker services"""

    def get_services_from_id(id):
        """Create services object from one docker service"""

    def get_service_exposed_ports(id):
        """Get exposed ports from a swarm service ID"""
