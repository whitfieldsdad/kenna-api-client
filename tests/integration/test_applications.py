from tests.integration import INTEGRATION_TESTS_ENABLED
from unittest import TestCase
from kenna.api import Kenna

import unittest


class ApplicationIntegrationTestCases(TestCase):
    kenna_api = None

    @classmethod
    def setUpClass(cls):
        if not INTEGRATION_TESTS_ENABLED:
            raise unittest.SkipTest("Integration tests are disabled - set ENABLE_INTEGRATION_TESTS=1 to enable them")

        cls.kenna_api = Kenna()
        try:
            next(cls.kenna_api.iter_applications(limit=1))
        except StopIteration:
            raise unittest.SkipTest("No applications found")

    def test_get_applications(self):
        applications = list(self.kenna_api.iter_applications(limit=1))
        self.assertGreater(len(applications), 0)
        self.assertTrue(all(isinstance(application, dict) for application in applications))

    def test_get_application(self):
        a = next(self.kenna_api.iter_applications(limit=1))
        self.assertIsNotNone(a)

        b = self.kenna_api.get_application(application_id=a['id'])
        self.assertIsNotNone(b)
        self.assertEqual(a['id'], b['id'])

    def test_count_applications(self):
        _ = self.kenna_api.count_applications()
