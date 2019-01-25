"""Define Node model object"""
import ipaddress
import re
from discovery.layers.infrastructure.exceptions import InvalidIPAddress


class Node:
    """Node object"""

    def __init__(self, name, address, id=None, nodeID=None, tags=()):
        self._name = name
        self._id = id
        self._nodeID = nodeID
        self._address = self._set_address(address)
        self._tags = tags if isinstance(tags, list) else []

    @property
    def name(self):
        """
        Node hostname

        :type self: Node
        :rtype: string
        """
        return self._name

    @property
    def id(self):
        """
        service id

        :type self: Service
        :rtype: int
        """
        return self._id

    @property
    def nodeID(self):
        """
        node id

        :type self: Service
        :rtype: int
        """
        return self._nodeID

    @property
    def tags(self):
        """
        service tag

        :type self: Service
        :rtype: list
        """
        return self._tags

    @property
    def address(self):
        """
        Node IP address

        :type self: Node
        :rtype: string
        """
        return self._address

    @staticmethod
    def _set_address(address):
        if address == '0.0.0.0':
            raise InvalidIPAddress(address)

        if address is not None:
            regex_address = re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", address)

            if regex_address is not None:
                return ipaddress.ip_address(address)

            return address

        return None
