# pylint: skip-file
"""Implement Service interface to to manage docker service"""
from zope.interface import Interface
from typing import Union


class SwarmInterface(Interface):
    """Interface to manage docker service"""

    def get_services_from_id(self, id):
        """Get services from a swarm service ID"""

    def get_containers_from_filters(self, filters: dict) -> Union[list, None]:
        """Get all containers of a service from filters"""
