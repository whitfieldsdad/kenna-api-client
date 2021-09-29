from unittest import TestCase
from kenna.api import Kenna
from tests.integration import INTEGRATION_TESTS_ENABLED

import unittest


class RoleIntegrationTestCases(TestCase):
    kenna_api = None

    @classmethod
    def setUpClass(cls):
        if not INTEGRATION_TESTS_ENABLED:
            raise unittest.SkipTest("Integration tests are disabled - set ENABLE_INTEGRATION_TESTS=1 to enable them")

        cls.kenna_api = Kenna()
        try:
            next(cls.kenna_api.iter_roles())
        except StopIteration:
            raise unittest.SkipTest("No roles found")

    def test_get_roles(self):
        roles = self.kenna_api.get_roles(limit=1)
        self.assertGreater(len(roles), 0)
        self.assertTrue(all(isinstance(role, dict) for role in roles))

    def test_get_role(self):
        roles = self.kenna_api.get_roles()
        self.assertIsInstance(roles, list)
        self.assertGreater(len(roles), 0)

        for a in roles:
            with self.subTest(role_id=a['id']):
                b = self.kenna_api.get_role(role_id=a['id'])
                if b:
                    self.assertEqual(a['id'], b['id'])
                    break
