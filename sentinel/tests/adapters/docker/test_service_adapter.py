import unittest
from adapters.docker.service_adapter import ServiceAdapter
from exceptions import NotImplementedException


class TestServiceAdapter(unittest.TestCase):
    def setUp(self):
        class NewServiceAdapter(ServiceAdapter):
            def __init__(self):
                pass

        self.service_adapter = NewServiceAdapter()

    def test_get_services_not_implemented(self):
        with self.assertRaises(NotImplementedException) as e:
            self.service_adapter.get_services()
            self.assertEquals(
                "Methode get_services is not implemented for NewServiceAdapter",
                e.message
            )

    def test_get_services_from_id_not_implemented(self):
        with self.assertRaises(NotImplementedException) as e:
            self.service_adapter.get_services_from_id()
            self.assertEquals(
                "Methode get_services_from_id is not implemented for NewServiceAdapter",
                e.message
            )

    def test_get_tags(self):
        self.assertEqual(
            ['http'],
            self.service_adapter._get_tags(labels={'service_tags': 'http', 'service_443_tags': 'https'}, envs=['service_80_tags=http'], internal_port=80)
        )

    def test_get_name_from_label_and_envs__labels_only(self):
        self.assertEqual(
            'hello',
            self.service_adapter._get_name_from_label_and_envs(labels={'service_name': 'hello'}, envs=[], internal_port=80)
        )

    def test_get_name_from_label_and_envs__envs_only(self):
        self.assertEqual(
            'hello',
            self.service_adapter._get_name_from_label_and_envs(labels={}, envs=['service_80_name=hello'], internal_port=80)
        )

    def test_has_to_be_registred_true(self):
        self.assertEqual(
            True,
            self.service_adapter._has_to_be_registred(labels={'not_register': 1, 'service_443_name': 'hello'}, envs=[], internal_port=443)
        )

    def test_has_to_be_registred_false(self):
        self.assertEqual(
            False,
            self.service_adapter._has_to_be_registred(labels={'not_register': 1, 'service_443_name': 'hello'}, envs=[], internal_port=80)
        )

    def test__trim_service_name(self):
        name = "service@$-1.test_again"
        self.assertEqual(
            'service-1.test-again',
            self.service_adapter._trim_service_name(name)
        )
