from orchestrators.orchestrator import Orchestrator
from exceptions import NotImplementedException
import unittest


class TestOrchestrator(unittest.TestCase):
    def setUp(self):

        class NewOrchestrator(Orchestrator):
            def __init__(self):
                pass

        self.orchestrator = NewOrchestrator()

    def test_listen_events_not_implemented(self):
        with self.assertRaises(NotImplementedException) as e:
            self.orchestrator.listen_events()
            self.assertEquals(
                "Methode listen_events is not implemented for NewOrchestrator",
                e.message
            )

    def test_get_services_not_implemented(self):
        with self.assertRaises(NotImplementedException) as e:
            self.orchestrator.get_services()
            self.assertEquals(
                "Methode get_services is not implemented for NewOrchestrator",
                e.message
            )

    def test_get_service_not_implemented(self):
        with self.assertRaises(NotImplementedException) as e:
            self.orchestrator.get_service()
            self.assertEquals(
                "Methode get_service is not implemented for NewOrchestrator",
                e.message
            )

    def test_get_service_tag_to_remove_not_implemented(self):
        with self.assertRaises(NotImplementedException) as e:
            self.orchestrator.get_service_tag_to_remove()
            self.assertEquals(
                "Methode get_service_tag_to_remove is not implemented for NewOrchestrator",
                e.message
            )
