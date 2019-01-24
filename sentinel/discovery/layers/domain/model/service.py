"""Define Service model object"""


class Service:
    """Service object"""

    def __init__(self, name, port=None, tags=(), nodes=(), running_containers=()):
        self._name = name
        self._port = port
        self._tags = tags if isinstance(tags, list) else []
        self._nodes = nodes if isinstance(nodes, list) else []
        self._running_containers = running_containers if isinstance(running_containers, list) else []

    @property
    def name(self):
        """
        service name

        :type self: Service
        :rtype: string
        """
        return self._name

    @property
    def port(self):
        """
        service port

        :type self: Service
        :rtype: int
        """
        return self._port

    @property
    def tags(self):
        """
        service tag

        :type self: Service
        :rtype: list
        """
        return self._tags

    @property
    def nodes(self):
        """
        Nodes where running service

        :type self: Service
        :rtype: list
        """
        return self._nodes

    @property
    def running_containers(self):
        """
        Containers running from service

        :type self: Service
        :rtype: list
        """
        return self._running_containers

    def set_port(self, port):
        """
        Set service port

        :type self: Service
        """
        self._port = port
