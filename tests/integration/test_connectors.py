from unittest import TestCase
from kenna.api import Kenna
from tests.integration import INTEGRATION_TESTS_ENABLED

import unittest


class ConnectorIntegrationTestCases(TestCase):
    kenna_api = None

    @classmethod
    def setUpClass(cls):
        if not INTEGRATION_TESTS_ENABLED:
            raise unittest.SkipTest("Integration tests are disabled - set ENABLE_INTEGRATION_TESTS=1 to enable them")

        cls.kenna_api = Kenna()

        #: At least one connector is required.
        try:
            next(cls.kenna_api.iter_connectors(limit=1))
        except StopIteration:
            raise unittest.SkipTest("No connectors found")

        #: At least one connector run is required.
        try:
            next(cls.kenna_api.iter_connector_runs())
        except StopIteration:
            raise unittest.SkipTest("No connector runs found")

    def test_get_connectors(self):
        connectors = list(self.kenna_api.iter_connectors())
        self.assertGreater(len(connectors), 0)
        self.assertTrue(all(isinstance(connector, dict) for connector in connectors))

    def test_get_connector(self):
        connector = next(self.kenna_api.iter_connectors())
        self.assertIsNotNone(connector)

        connector = self.kenna_api.get_connector(connector_id=connector['id'])
        self.assertIsNotNone(connector)

    def test_get_connector_runs_by_connector_id(self):
        mapping = self.kenna_api.get_connector_runs_by_connector_id()
        self.assertIsInstance(mapping, dict)

        for runs in mapping.values():
            for run in runs:
                self.assertIsInstance(run, dict)
                self.assertTrue(run)

    def test_get_connector_run(self):
        runs = self.kenna_api.get_connector_runs_by_connector_id()
        if not runs:
            raise unittest.SkipTest("No connector runs found")

        connector_id, connector_runs = runs.popitem()
        connector_run_id = next(iter(connector_runs))['id']

        connector_run = self.kenna_api.get_connector_run(connector_id=connector_id, connector_run_id=connector_run_id)
        self.assertEqual(connector_run_id, connector_run['id'])

    def test_count_connectors(self):
        _ = self.kenna_api.count_connectors()

    def test_count_connector_runs(self):
        _ = self.kenna_api.count_connector_runs()
