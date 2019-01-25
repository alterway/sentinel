from discovery.layers.infrastructure.api.consul.query import Query
from discovery.layers.infrastructure.api.consul.command import Command


class ApiConsulFactory:

    @staticmethod
    def query() -> Query:
        """Return the query service of consul api"""
        return Query()

    @staticmethod
    def command() -> Command:
        """Return the command service of consul api"""
        return Command()

