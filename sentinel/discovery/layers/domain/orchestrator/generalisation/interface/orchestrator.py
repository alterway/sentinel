# pylint: skip-file
"""Implement Orestrator interface to inherit in orchestrator adapters"""
from zope.interface import Interface


class OrchestratorInterface(Interface):
    """Interface to create orchestrator adapters"""

    def listen_events(*args, **kwargs):
        """Listen docker events"""

    def get_services(*args, **kwargs):
        """Get docker running services"""

    def get_service(*args, **kwargs):
        """Get services objects from one docker service"""

    def get_service_tag_to_remove(*args, **kwargs):
        """Get tag for service to remove"""
