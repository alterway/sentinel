class Config():
    def __init__(self, deployment_type="docker-compose", orchestrator="swarm", backend="consul"):
        deployment_type_choices = ["swarmservice", "docker-compose"]
        if deployment_type not in deployment_type_choices:
            raise Exception("%s is not a valid deployment_type : %s" % (
                deployment_type, deployment_type_choices
            ))

        self.orchestrator = orchestrator
        self.backend = backend
        self.deployment_type = deployment_type


class SwarmNodesConfig():
    def __init__(self, managers_hostname, workers_hostname=[]):
        self.managers_hostname = managers_hostname
        self.workers_hostname = workers_hostname
