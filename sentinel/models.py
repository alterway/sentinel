"""Define sentinel models objects"""
import ipaddress

from exceptions import InvalidIPAddress


class Service:
    """Service object"""
    def __init__(self, name, port=None, tags=(), nodes=()):
        self._name = name
        self._port = port
        self._tags = tags if isinstance(tags, list) else []
        self._nodes = nodes if isinstance(nodes, list) else []

    @property
    def name(self):
        """service name"""
        return self._name

    @property
    def port(self):
        """Service exposed port"""
        return self._port

    @property
    def tags(self):
        """Service tags"""
        return self._tags

    @property
    def nodes(self):
        """Nodes where running service"""
        return self._nodes

    def set_port(self, port):
        """Set service port"""
        self._port = port


class Node:
    """Node object"""
    def __init__(self, name, address):
        self._name = name
        self._address = self._set_address(address)

    @property
    def name(self):
        """Node hostname"""
        return self._name

    @property
    def address(self):
        """Node IP address"""
        return self._address

    @staticmethod
    def _set_address(address):
        if address == '0.0.0.0':
            raise InvalidIPAddress(address)

        return ipaddress.ip_address(address)
