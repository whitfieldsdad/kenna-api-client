from unittest import TestCase
from kenna.api import Kenna
from tests.integration import INTEGRATION_TESTS_ENABLED

import unittest


class DashboardGroupIntegrationTestCases(TestCase):
    kenna_api = None

    @classmethod
    def setUpClass(cls):
        if not INTEGRATION_TESTS_ENABLED:
            raise unittest.SkipTest("Integration tests are disabled - set ENABLE_INTEGRATION_TESTS=1 to enable them")

        cls.kenna_api = Kenna()
        try:
            next(cls.kenna_api.iter_dashboard_groups(limit=1))
        except StopIteration:
            raise unittest.SkipTest("No dashboard groups found")

    def test_get_dashboard_groups(self):
        dashboard_groups = list(self.kenna_api.iter_dashboard_groups(limit=1))
        self.assertGreater(len(dashboard_groups), 0)
        self.assertTrue(all(isinstance(asset, dict) for asset in dashboard_groups))

    def test_get_dashboard_group(self):
        a = next(self.kenna_api.iter_dashboard_groups(limit=1))
        self.assertIsNotNone(a)

        b = self.kenna_api.get_dashboard_group(dashboard_group_id=a['id'])
        self.assertIsNotNone(b)
        self.assertEqual(a['id'], b['id'])

    def test_count_dashboard_groups(self):
        _ = self.kenna_api.count_dashboard_groups()
