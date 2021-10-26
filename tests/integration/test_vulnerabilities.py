from unittest import TestCase
from kenna.api import Kenna
from tests.integration import INTEGRATION_TESTS_ENABLED

import unittest


class VulnerabilityIntegrationTestCases(TestCase):
    kenna_api = None

    @classmethod
    def setUpClass(cls):
        if not INTEGRATION_TESTS_ENABLED:
            raise unittest.SkipTest("Integration tests are disabled - set ENABLE_INTEGRATION_TESTS=1 to enable them")

        cls.kenna_api = Kenna()
        try:
            next(cls.kenna_api.iter_vulnerabilities(limit=1))
        except StopIteration:
            raise unittest.SkipTest("No vulnerabilities found")

    def test_get_vulnerabilities(self):
        vulnerabilities = list(self.kenna_api.iter_vulnerabilities(limit=1))
        self.assertGreater(len(vulnerabilities), 0)
        self.assertTrue(all(isinstance(vulnerability, dict) for vulnerability in vulnerabilities))

    def test_get_vulnerability(self):
        a = next(self.kenna_api.iter_vulnerabilities(limit=1))
        self.assertIsNotNone(a)

        b = self.kenna_api.get_vulnerability(vulnerability_id=a['id'])
        self.assertIsNotNone(b)
        self.assertEqual(a['id'], b['id'])

    def test_count_vulnerabilities(self):
        _ = self.kenna_api.count_vulnerabilities()
