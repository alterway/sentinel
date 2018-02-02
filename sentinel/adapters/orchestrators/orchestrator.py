from exceptions import NotImplemented


class OrchestratorAdapter():

    def get_services(self):
        raise NotImplemented('Method get_services() not implemented')

    def get_service(self):
        raise NotImplemented('Method get_service() not implemented')

    def get_service_tag_to_remove(self):
        raise NotImplemented('Method get_service() not implemented')
