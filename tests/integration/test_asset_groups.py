from unittest import TestCase
from kenna.api import Kenna
from tests.integration import INTEGRATION_TESTS_ENABLED

import unittest


class AssetGroupIntegrationTestCases(TestCase):
    kenna_api = None

    @classmethod
    def setUpClass(cls):
        if not INTEGRATION_TESTS_ENABLED:
            raise unittest.SkipTest("Integration tests are disabled - set ENABLE_INTEGRATION_TESTS=1 to enable them")

        cls.kenna_api = Kenna()
        try:
            next(cls.kenna_api.iter_asset_groups(limit=1))
        except StopIteration:
            raise unittest.SkipTest("No asset groups found")

    def test_get_asset_groups(self):
        asset_groups = list(self.kenna_api.iter_asset_groups(limit=1))
        self.assertGreater(len(asset_groups), 0)
        self.assertTrue(all(isinstance(asset_group, dict) for asset_group in asset_groups))

    def test_get_asset_group(self):
        a = next(self.kenna_api.iter_asset_groups(limit=1))
        self.assertIsNotNone(a)

        b = self.kenna_api.get_asset_group(asset_group_id=a['id'])
        self.assertIsNotNone(b)
        self.assertEqual(a['id'], b['id'])

    def test_count_asset_groups(self):
        _ = self.kenna_api.count_asset_groups()
