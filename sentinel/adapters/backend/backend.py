from sentinel.exceptions import NotImplemented


class BackendAdapter():
    def get_services(self):
        raise NotImplemented("The method get_services() is not implemented for this backend")

    def register_service(self):
        raise NotImplemented("The method register_service() is not implemented for this backend")
