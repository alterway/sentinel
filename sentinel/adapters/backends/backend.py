from utils.dependencies_injection import inject_param


class BackendAdapter():

    @classmethod
    @inject_param("not_implemented")
    def get_services(cls, not_implemented=None):
        not_implemented(cls.__class__.__name__)

    @classmethod
    @inject_param("not_implemented")
    def register_service(cls, not_implemented=None):
        not_implemented(cls.__class__.__name__)

    @classmethod
    @inject_param("not_implemented")
    def deregister_node(cls, not_implemented=None):
        not_implemented(cls.__class__.__name__)
