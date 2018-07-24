import unittest
from zope.interface import implementer
from zope.interface.exceptions import BrokenImplementation
from zope.interface.verify import verifyObject

from orchestrators.orchestrator import Orchestrator


class TestOrchestrator(unittest.TestCase):
    def setUp(self):

        @implementer(Orchestrator)
        class NewBadOrchestrator(object):
            def __init__(self):
                pass

        @implementer(Orchestrator)
        class NewGoodOrchestrator(object):
            @classmethod
            def listen_events(*args, **kwargs):
                return "Listen docker events"

            @classmethod
            def get_services(*args, **kwargs):
                return "Get docker running services"

            @classmethod
            def get_service(*args, **kwargs):
                return "Get services objects from one docker service"

            @classmethod
            def get_service_tag_to_remove(*args, **kwargs):
                return "Get tag for service to remove"

        self.bad_orchestrator = NewBadOrchestrator()
        self.good_orchestrator = NewGoodOrchestrator()

    def test_bad_interface_implementation(self):
        with self.assertRaises(BrokenImplementation):
            verifyObject(Orchestrator, self.bad_orchestrator)

    def test_interface_implementation_success(self):
        self.assertEqual(True, verifyObject(Orchestrator, self.good_orchestrator))
