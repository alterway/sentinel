from zope.interface import Interface


class Orchestrator(Interface):  # pylint: disable-msg=inherit-non-class
    """Interface to create orchestrator adapters"""

    def listen_events(*args, **kwargs):  # pylint: disable-msg=no-method-argument
        """Listen docker events"""

    def get_services(*args, **kwargs):  # pylint: disable-msg=no-method-argument
        """Get docker running services"""

    def get_service(*args, **kwargs):  # pylint: disable-msg=no-method-argument
        """Get services objects from one docker service"""

    def get_service_tag_to_remove(*args, **kwargs):  # pylint: disable-msg=no-method-argument
        """Get tag for service to remove"""
