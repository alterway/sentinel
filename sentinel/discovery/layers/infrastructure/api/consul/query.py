import requests
from ddd_domain_driven_design.domain.utils.multiton import Multiton
from discovery.layers.domain.model.service import Service


class Query(metaclass=Multiton):
    """
    Adapter to request Query Consul API
    """

    @staticmethod
    def get_catalog_services(address):
        response = requests.get('http://%s/v1/catalog/services' % address).json()
        services = [
            Service(name=key, tags=response[key], nodes=[])
            for key in response.keys()
        ]

        return services

    @staticmethod
    def get_catalog_service(address, service_name):
        return requests.get(
            'http://%s/v1/catalog/service/%s' % (
                address, service_name
            )
        ).json()

