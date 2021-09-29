from unittest import TestCase
from kenna.api import Kenna
from tests.integration import INTEGRATION_TESTS_ENABLED

import unittest


class UserIntegrationTestCases(TestCase):
    kenna_api = None

    @classmethod
    def setUpClass(cls):
        if not INTEGRATION_TESTS_ENABLED:
            raise unittest.SkipTest("Integration tests are disabled - set ENABLE_INTEGRATION_TESTS=1 to enable them")

        cls.kenna_api = Kenna()
        try:
            next(cls.kenna_api.iter_users())
        except StopIteration:
            raise unittest.SkipTest("No users found")

    def test_get_users(self):
        users = self.kenna_api.get_users(limit=1)
        self.assertGreater(len(users), 0)
        self.assertTrue(all(isinstance(user, dict) for user in users))

    def test_get_user(self):
        a = next(self.kenna_api.iter_users(limit=1))
        self.assertIsNotNone(a)

        b = self.kenna_api.get_user(user_id=a['id'])
        self.assertIsNotNone(b)
        self.assertEqual(a['id'], b['id'])
