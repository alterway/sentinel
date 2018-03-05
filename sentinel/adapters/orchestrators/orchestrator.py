from exceptions import NotImplemented


class OrchestratorAdapter():
    """Interface to create orchestrator adapters
    """

    @staticmethod
    def process_event(event):
        raise NotImplemented('Method process_event() not implemented')

    @staticmethod
    def get_services():
        raise NotImplemented('Method get_services() not implemented')

    @staticmethod
    def get_service():
        raise NotImplemented('Method get_service() not implemented')

    @staticmethod
    def get_service_tag_to_remove():
        raise NotImplemented('Method get_service_tag_to_remove() not implemented')
