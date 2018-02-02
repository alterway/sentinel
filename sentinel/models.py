
class Service(object):
    def __init__(self, name, port=None, tags=[], nodes=[]):
        self.name = name
        self.port = port
        self.tags = tags
        self.nodes = nodes

class Node(object):
    def __init__(self, name, address):
        self.name = name
        self.address = address
