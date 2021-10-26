from unittest import TestCase
from kenna.api import Kenna
from tests.integration import INTEGRATION_TESTS_ENABLED

import unittest


class AssetIntegrationTestCases(TestCase):
    kenna_api = None

    @classmethod
    def setUpClass(cls):
        if not INTEGRATION_TESTS_ENABLED:
            raise unittest.SkipTest("Integration tests are disabled - set ENABLE_INTEGRATION_TESTS=1 to enable them")

        cls.kenna_api = Kenna()
        try:
            next(cls.kenna_api.iter_assets(limit=1))
        except StopIteration:
            raise unittest.SkipTest("No assets found")

    def test_get_assets(self):
        assets = list(self.kenna_api.iter_assets(limit=1))
        self.assertGreater(len(assets), 0)
        self.assertTrue(all(isinstance(asset, dict) for asset in assets))

    def test_get_asset(self):
        a = next(self.kenna_api.iter_assets(limit=1))
        self.assertIsNotNone(a)

        b = self.kenna_api.get_asset(asset_id=a['id'])
        self.assertIsNotNone(b)
        self.assertEqual(a['id'], b['id'])

    def test_count_assets(self):
        _ = self.kenna_api.count_assets()
