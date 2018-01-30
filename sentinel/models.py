
class Service(object):
    def __init__(self, name, port, tags=[], nodes=[]):
        self.name = name
        self.port = None
        self.tags = tags
        self.nodes = nodes

class Node(object):
    def __init__(self, name, address):
        self.name = name
        self.address = address
