from unittest import TestCase
from kenna.api import Kenna
from tests.integration import INTEGRATION_TESTS_ENABLED

import unittest


class FixIntegrationTestCases(TestCase):
    kenna_api = None

    @classmethod
    def setUpClass(cls):
        if not INTEGRATION_TESTS_ENABLED:
            raise unittest.SkipTest("Integration tests are disabled - set ENABLE_INTEGRATION_TESTS=1 to enable them")

        cls.kenna_api = Kenna()
        try:
            next(cls.kenna_api.iter_fixes(limit=1))
        except StopIteration:
            raise unittest.SkipTest("No fixes found")

    def test_get_fixes(self):
        fixes = list(self.kenna_api.iter_fixes(limit=1))
        self.assertGreater(len(fixes), 0)
        self.assertTrue(all(isinstance(fix, dict) for fix in fixes))

    def test_get_fix(self):
        a = next(self.kenna_api.iter_fixes(limit=1))
        self.assertIsNotNone(a)

        b = self.kenna_api.get_fix(fix_id=a['id'])
        self.assertIsNotNone(b)
        self.assertEqual(a['id'], b['id'])

    def test_count_fixes(self):
        _ = self.kenna_api.count_fixes()
