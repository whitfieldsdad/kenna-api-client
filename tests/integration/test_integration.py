from kenna.api import Kenna
from kenna.authentication import DEFAULT_API_KEY

import unittest
import logging

logger = logging.getLogger(__name__)

SEARCH_RESULT_LIMIT = 50


class AssetIntegrationTests(unittest.TestCase):
    kenna_api = None

    @classmethod
    def setUpClass(cls):
        if not DEFAULT_API_KEY:
            raise unittest.SkipTest("An API key is required")

        cls.kenna_api = Kenna(api_key=DEFAULT_API_KEY)

    def test_get_applications(self):
        rows = self.kenna_api.get_applications(limit=SEARCH_RESULT_LIMIT)
        self.assertGreater(len(rows), 0)
        self.assertLessEqual(len(rows), SEARCH_RESULT_LIMIT)

    def test_get_assets(self):
        rows = self.kenna_api.get_assets(limit=SEARCH_RESULT_LIMIT)
        self.assertGreater(len(rows), 0)
        self.assertLessEqual(len(rows), SEARCH_RESULT_LIMIT)

    def test_get_connectors(self):
        rows = self.kenna_api.get_connectors(limit=SEARCH_RESULT_LIMIT)
        self.assertGreater(len(rows), 0)
        self.assertLessEqual(len(rows), SEARCH_RESULT_LIMIT)

    def test_get_connector_runs(self):
        rows = self.kenna_api.get_connector_runs(limit=SEARCH_RESULT_LIMIT)
        self.assertGreater(len(rows), 0)
        self.assertLessEqual(len(rows), SEARCH_RESULT_LIMIT)

    def test_get_dashboard_groups(self):
        rows = self.kenna_api.get_dashboard_groups(limit=SEARCH_RESULT_LIMIT)
        self.assertGreater(len(rows), 0)
        self.assertLessEqual(len(rows), SEARCH_RESULT_LIMIT)

    def test_get_fixes(self):
        rows = self.kenna_api.get_fixes(limit=SEARCH_RESULT_LIMIT)
        self.assertGreater(len(rows), 0)
        self.assertLessEqual(len(rows), SEARCH_RESULT_LIMIT)

    def test_get_users(self):
        rows = self.kenna_api.get_users(limit=SEARCH_RESULT_LIMIT)
        self.assertGreater(len(rows), 0)
        self.assertLessEqual(len(rows), SEARCH_RESULT_LIMIT)

    def test_get_roles(self):
        rows = self.kenna_api.get_roles(limit=SEARCH_RESULT_LIMIT)
        self.assertGreater(len(rows), 0)
        self.assertLessEqual(len(rows), SEARCH_RESULT_LIMIT)

    def test_get_vulnerabilities(self):
        rows = self.kenna_api.get_vulnerabilities(limit=SEARCH_RESULT_LIMIT)
        self.assertGreater(len(rows), 0)
        self.assertLessEqual(len(rows), SEARCH_RESULT_LIMIT)
