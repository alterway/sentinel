from service.base import ServiceBase
import unittest


class TestServiceBase(unittest.TestCase):
    def setUp(self):
        class NewServiceAdapter(ServiceBase):
            def __init__(self):
                pass

        self.service_adapter = NewServiceAdapter()

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
