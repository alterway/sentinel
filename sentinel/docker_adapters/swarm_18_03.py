from docker_adapters.swarm_adapter import SwarmAdapter


class SwarmVersionAdapter(SwarmAdapter):
    """SwarmVersionAdapter for docker server version 18.03.*

    No method in this class because all is in base
    To Create an adapter for another version :
        - create file docker_adapters.swarm_version.py
        - create class SwarmVersionAdapter inherited SwarmAdapter
        - redifine methods if method in DockerAdapter not compatible
    """
    pass
