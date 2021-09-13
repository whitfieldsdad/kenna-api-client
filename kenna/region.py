from typing import Optional

GLOBAL = "global"
CA = "ca"
EU = "eu"
US = "us"

API_ENDPOINTS_BY_REGION = {
    GLOBAL: 'https://api.kennasecurity.com',
    US: 'https://api.us.kennasecurity.com',
    EU: 'https://api.eu.kennasecurity.com',
    CA: 'https://api.ca.kennasecurity.com',
}

ALL_REGIONS = list(API_ENDPOINTS_BY_REGION.keys())

DEFAULT_REGION = GLOBAL


def get_regional_endpoint(region: Optional[str] = None) -> str:
    return API_ENDPOINTS_BY_REGION[region or DEFAULT_REGION]


def verify_region_name(region: str) -> str:
    if region not in ALL_REGIONS:
        raise ValueError("Unsupported region: {} (supported: {})".format(region, ALL_REGIONS))
    return region
