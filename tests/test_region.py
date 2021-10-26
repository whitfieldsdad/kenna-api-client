from unittest import TestCase
from kenna.errors import InvalidRegionError
from kenna.region import ALL_ENDPOINTS, ALL_REGIONS, GLOBAL, US, EU, CA

import kenna.region


class RegionTestCases(TestCase):
    def test_get_endpoint(self):
        for region in ALL_REGIONS:
            endpoint = kenna.region.get_endpoint(region)
            self.assertIn(endpoint, ALL_ENDPOINTS)

    def test_validate_name(self):
        for region in [GLOBAL, US, EU, CA]:
            kenna.region.validate_name(region)

        with self.assertRaises(InvalidRegionError):
            kenna.region.validate_name('Bikini Bottom')