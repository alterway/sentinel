import unittest
from adapters.docker.service_adapter import ServiceAdapter


class TestServiceAdapter(unittest.TestCase):
    def setUp(self):
        self.service_adapter = ServiceAdapter()

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
