from docker_adapters.base import DockerAdapter, SwarmAdapter


class DockerVersionAdapter(DockerAdapter):
    """DockerVersionAdapter for docker server version 18.03.*

    No method in this class because all is in base
    To Create an adapter for another version :
        - create file docker_adapters.docker_version.py
        - create class DockerVersionAdapter inherited DockerAdapter
        - redifine methods if method in DockerAdapter not compatible
    """
    pass


class SwarmVersionAdapter(SwarmAdapter):
    """SwarmVersionAdapter for docker server version 18.03.*

    No method in this class because all is in base
    To Create an adapter for another version :
        - create file docker_adapters.swarm_version.py
        - create class SwarmVersionAdapter inherited SwarmAdapter
        - redifine methods if method in DockerAdapter not compatible
    """
    pass
