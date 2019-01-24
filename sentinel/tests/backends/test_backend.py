from zope.interface import implementer
from zope.interface.exceptions import BrokenImplementation
from zope.interface.verify import verifyObject
import unittest

from discovery import Backend


class TestBackend(unittest.TestCase):
    def setUp(self):

        @implementer(Backend)
        class NewBadBackend(object):
            def __init__(self):
                pass

        @implementer(Backend)
        class NewGoodBackend(object):

            def __init__(self, address):
                self.address = address

            def get_services(self, docker_adapter=None, logger=None):
                """Get service in backend"""
                return "get services in the good backend"

            def register_service(self, service, logger=None):
                """Register a service in backend"""
                return "register service in the good backend"

            def deregister_node(self, service, logger=None):
                """Deregister a service in backend"""
                return "deregister service in the good backend"

        self.badbackend = NewBadBackend()
        self.goodbackend = NewGoodBackend("http://backend")

    def test_interface_implementation_failed(self):
        with self.assertRaises(BrokenImplementation):
            verifyObject(Backend, self.badbackend)

    def test_interface_implementation_success(self):
        self.assertEqual(True, verifyObject(Backend, self.goodbackend))
