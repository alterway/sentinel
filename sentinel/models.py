from exceptions import InvalidIPAddress
import ipaddress


class Service(object):
    def __init__(self, name, port=None, tags=(), nodes=()):
        self.name = name
        self.port = port
        self.tags = tags if isinstance(tags, list) else []
        self.nodes = nodes if isinstance(nodes, list) else []


class Node(object):
    def __init__(self, name, address):
        if address == '0.0.0.0':
            raise InvalidIPAddress(address)

        self.name = name
        self.address = ipaddress.ip_address(address)
