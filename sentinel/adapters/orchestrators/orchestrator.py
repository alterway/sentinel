from utils.dependencies_injection import inject_param


class OrchestratorAdapter():
    """Interface to create orchestrator adapters
    """
    @classmethod
    @inject_param("not_implemented")
    def process_event(cls, not_implemented=None):
        not_implemented(cls.__class__.__name__)

    @classmethod
    @inject_param("not_implemented")
    def get_services(cls, not_implemented=None):
        not_implemented(cls.__class__.__name__)

    @classmethod
    @inject_param("not_implemented")
    def get_service(cls, not_implemented=None):
        not_implemented(cls.__class__.__name__)

    @classmethod
    @inject_param("not_implemented")
    def get_service_tag_to_remove(cls, not_implemented=None):
        not_implemented(cls.__class__.__name__)
