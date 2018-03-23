import unittest
from adapters.backends.backend import BackendAdapter
from exceptions import NotImplementedException


class TestOrchestrator(unittest.TestCase):
    def setUp(self):

        class NewBackend(BackendAdapter):
            def __init__(self):
                pass

        self.backend = NewBackend()

    def test_get_services_not_implemented(self):
        with self.assertRaises(NotImplementedException) as e:
            self.backend.get_services()
            self.assertEqual(
                "Methode get_services not implemented for NewBackend",
                e.message
            )

    def test_register_service_not_implemented(self):
        with self.assertRaises(NotImplementedException) as e:
            self.backend.register_service()
            self.assertEqual(
                "Methode register_service not implemented for NewBackend",
                e.message
            )

    def test_deregister_node_not_implemented(self):
        with self.assertRaises(NotImplementedException) as e:
            self.backend.deregister_node()
            self.assertEqual(
                "Methode deregister_node not implemented for NewBackend",
                e.message
            )
