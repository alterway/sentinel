from exceptions import NotImplemented


class OrchestratorAdapter():

    def process_event(self, event):
        raise NotImplemented('Method process_event() not implemented')

    def get_services(self):
        raise NotImplemented('Method get_services() not implemented')

    def get_service(self):
        raise NotImplemented('Method get_service() not implemented')

    def get_service_tag_to_remove(self):
        raise NotImplemented('Method get_service_tag_to_remove() not implemented')
