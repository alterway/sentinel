import unittest
from adapters.orchestrators.orchestrator import OrchestratorAdapter
from exceptions import NotImplementedException


class TestOrchestrator(unittest.TestCase):
    def setUp(self):

        class NewOrchestrator(OrchestratorAdapter):
            def __init__(self):
                pass

        self.orchestrator = NewOrchestrator()

    def test_process_event_not_implemented(self):
        with self.assertRaises(NotImplementedException) as e:
            self.orchestrator.process_event()
            self.assertEquals(
                "Methode process_event is not implemented for NewOrchestrator",
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
