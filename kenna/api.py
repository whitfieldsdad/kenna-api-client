import collections
from typing import Optional, Iterator, Iterable, List, Set, Dict
from hodgepodge.requests import DEFAULT_MAX_RETRIES_ON_REDIRECT, DEFAULT_MAX_RETRIES_ON_CONNECTION_ERRORS, \
    DEFAULT_MAX_RETRIES_ON_READ_ERRORS, DEFAULT_BACKOFF_FACTOR
from kenna import DEFAULT_API_KEY, DEFAULT_REGION
from kenna.constants import APPLICATIONS, ASSETS, CONNECTORS, CONNECTOR_RUNS, \
    DASHBOARD_GROUPS, FIXES, VULNERABILITIES, USERS, ROLES, ASSET_GROUPS, COLLECTION_NAMES, OBJECT_TYPES

import datetime
import hodgepodge.archives
import hodgepodge.compression
import hodgepodge.files
import hodgepodge.hashing
import hodgepodge.network
import hodgepodge.numbers
import hodgepodge.patterns
import hodgepodge.requests
import hodgepodge.time
import hodgepodge.types
import hodgepodge.web
import itertools
import kenna.authentication
import kenna.region
import logging
import requests
import urllib.parse


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class Kenna:
    def __init__(
            self,
            api_key: str = DEFAULT_API_KEY,
            region: str = DEFAULT_REGION,
            max_retries_on_connection_errors: int = DEFAULT_MAX_RETRIES_ON_CONNECTION_ERRORS,
            max_retries_on_read_errors: int = DEFAULT_MAX_RETRIES_ON_READ_ERRORS,
            max_retries_on_redirects: int = DEFAULT_MAX_RETRIES_ON_REDIRECT,
            backoff_factor: float = DEFAULT_BACKOFF_FACTOR):

        self.region = region = kenna.region.validate_name(region)
        self.url = kenna.region.get_endpoint(region)

        self.session = requests.Session()
        self.session.headers['X-Risk-Token'] = kenna.authentication.validate_api_key(api_key)

        auto_retry_policy = hodgepodge.requests.get_automatic_retry_policy(
            max_retries_on_connection_errors=max_retries_on_connection_errors,
            max_retries_on_read_errors=max_retries_on_read_errors,
            max_retries_on_redirects=max_retries_on_redirects,
            backoff_factor=backoff_factor,
        )
        hodgepodge.requests.attach_http_request_policies_to_session(session=self.session, policies=[auto_retry_policy])

    def _get_object(self, url: str) -> Optional[dict]:
        response = self.session.get(url)
        if response.status_code == 404:
            return None

        response.raise_for_status()
        data = response.json()
        if len(data.keys()) == 1:
            _, v = data.popitem()
            return v
        else:
            for k, v in data.items():
                if k in OBJECT_TYPES:
                    return v
            else:
                return data

    def _get_response(self, url: str) -> Optional[dict]:
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def _iter_objects(self, url: str, params: Optional[dict] = None):
        params = params or {}

        response = self.session.get(url=url, params=params)
        response.raise_for_status()

        #: Read the first page of the response.
        data = response.json()
        if isinstance(data, list):
            for row in data:
                yield row

        elif isinstance(data, dict):
            for key, values in data.items():
                if key in COLLECTION_NAMES:
                    for value in values:
                        yield value

            #: Read any remaining pages (note that page numbers are 1-indexed).
            meta = data.get('meta')
            if meta:
                for page_number in range(2, meta['pages'] + 1):
                    params['page'] = page_number

                    response = self.session.get(url=url, params=params)
                    response.raise_for_status()

                    for (key, values) in response.json().items():
                        if key == 'meta':
                            continue

                        for value in values:
                            yield value
        else:
            raise TypeError("Received {} - expected one of {}".format(type(data).__name__, [t.__name__ for t in [dict, list]]))

    def get_application(self, application_id: int) -> Optional[dict]:
        url = urllib.parse.urljoin(self.url, '{}/{}'.format(APPLICATIONS, application_id))
        return self._get_object(url)

    def get_applications(
            self,
            application_ids: Optional[Iterable[int]] = None,
            application_names: Optional[Iterable[str]] = None,
            application_owners: Optional[Iterable[str]] = None,
            application_teams: Optional[Iterable[str]] = None,
            application_business_units: Optional[Iterable[str]] = None,
            min_application_risk_meter_score: Optional[int] = None,
            max_application_risk_meter_score: Optional[int] = None,
            min_asset_count: Optional[int] = None,
            max_asset_count: Optional[int] = None,
            min_vulnerability_count: Optional[int] = None,
            max_vulnerability_count: Optional[int] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_applications(
            application_ids=application_ids,
            application_names=application_names,
            application_owners=application_owners,
            application_teams=application_teams,
            application_business_units=application_business_units,
            min_application_risk_meter_score=min_application_risk_meter_score,
            max_application_risk_meter_score=max_application_risk_meter_score,
            min_asset_count=min_asset_count,
            max_asset_count=max_asset_count,
            min_vulnerability_count=min_vulnerability_count,
            max_vulnerability_count=max_vulnerability_count,
            limit=limit,
        ))

    def iter_applications(
            self,
            application_ids: Optional[Iterable[int]] = None,
            application_names: Optional[Iterable[str]] = None,
            application_owners: Optional[Iterable[str]] = None,
            application_teams: Optional[Iterable[str]] = None,
            application_business_units: Optional[Iterable[str]] = None,
            min_application_risk_meter_score: Optional[int] = None,
            max_application_risk_meter_score: Optional[int] = None,
            min_asset_count: Optional[int] = None,
            max_asset_count: Optional[int] = None,
            min_vulnerability_count: Optional[int] = None,
            max_vulnerability_count: Optional[int] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        i = 0
        url = urllib.parse.urljoin(self.url, APPLICATIONS)
        for app in self._iter_objects(url=url):

            #: Filter applications by ID.
            if application_ids and app['id'] not in application_ids:
                continue

            #: Filter applications by name.
            if application_names and not hodgepodge.patterns.str_matches_glob(app['name'], application_names):
                continue

            #: Filter applications by by owner.
            if application_owners and not hodgepodge.patterns.str_matches_glob(app['owner'], application_owners):
                continue

            #: Filter applications by team name.
            if application_teams and not hodgepodge.patterns.str_matches_glob(app['team_name'], application_teams):
                continue

            #: Filter application by business unit.
            if application_business_units and not hodgepodge.patterns.str_matches_glob(app['business_units'], application_business_units):
                continue

            #: Filter applications by meter score.
            if (min_application_risk_meter_score is not None or max_application_risk_meter_score is not None) and \
                    not hodgepodge.numbers.is_within_range(app['risk_meter_score'], min_application_risk_meter_score, max_application_risk_meter_score):
                continue

            #: Filter applications by vulnerability count.
            if min_vulnerability_count is not None or max_vulnerability_count is not None:
                if not hodgepodge.numbers.is_within_range(
                    value=app['total_vulnerability_count'],
                    minimum=min_vulnerability_count,
                    maximum=max_vulnerability_count,
                ):
                    continue

            #: Filter applications by asset count.
            if min_asset_count is not None or max_asset_count is not None:
                if not hodgepodge.numbers.is_within_range(app['asset_count'], min_asset_count, max_asset_count):
                    continue

            yield app

            if limit:
                i += 1
                if i >= limit:
                    return

    def get_asset(self, asset_id: int) -> Optional[dict]:
        url = urllib.parse.urljoin(self.url, '{}/{}'.format(ASSETS, asset_id))
        return self._get_object(url)

    def get_assets(
            self,
            asset_ids: Optional[Iterable[int]] = None,
            asset_group_ids: Optional[Iterable[int]] = None,
            asset_group_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            asset_hostnames: Optional[Iterable[str]] = None,
            asset_ip_addresses: Optional[Iterable[str]] = None,
            asset_mac_addresses: Optional[Iterable[str]] = None,
            min_asset_risk_meter_score: Optional[int] = None,
            max_asset_risk_meter_score: Optional[int] = None,
            min_asset_first_seen_time: Optional[datetime.datetime] = None,
            max_asset_first_seen_time: Optional[datetime.datetime] = None,
            min_asset_last_seen_time: Optional[datetime.datetime] = None,
            max_asset_last_seen_time: Optional[datetime.datetime] = None,
            min_asset_last_boot_time: Optional[datetime.datetime] = None,
            max_asset_last_boot_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_assets(
            asset_ids=asset_ids,
            asset_group_ids=asset_group_ids,
            asset_group_names=asset_group_names,
            asset_tags=asset_tags,
            asset_hostnames=asset_hostnames,
            asset_ip_addresses=asset_ip_addresses,
            asset_mac_addresses=asset_mac_addresses,
            min_asset_risk_meter_score=min_asset_risk_meter_score,
            max_asset_risk_meter_score=max_asset_risk_meter_score,
            min_asset_first_seen_time=min_asset_first_seen_time,
            max_asset_first_seen_time=max_asset_first_seen_time,
            min_asset_last_seen_time=min_asset_last_seen_time,
            max_asset_last_seen_time=max_asset_last_seen_time,
            min_asset_last_boot_time=min_asset_last_boot_time,
            max_asset_last_boot_time=max_asset_last_boot_time,
            limit=limit,
        ))

    def iter_assets(
            self,
            asset_ids: Optional[Iterable[int]] = None,
            asset_group_ids: Optional[Iterable[int]] = None,
            asset_group_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            asset_hostnames: Optional[Iterable[str]] = None,
            asset_ip_addresses: Optional[Iterable[str]] = None,
            asset_mac_addresses: Optional[Iterable[str]] = None,
            min_asset_risk_meter_score: Optional[int] = None,
            max_asset_risk_meter_score: Optional[int] = None,
            min_asset_first_seen_time: Optional[datetime.datetime] = None,
            max_asset_first_seen_time: Optional[datetime.datetime] = None,
            min_asset_last_seen_time: Optional[datetime.datetime] = None,
            max_asset_last_seen_time: Optional[datetime.datetime] = None,
            min_asset_last_boot_time: Optional[datetime.datetime] = None,
            max_asset_last_boot_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        i = 0
        url = urllib.parse.urljoin(self.url, ASSETS)
        for asset in self._iter_objects(url=url):

            #: Filter applications by ID.
            if asset_ids and asset['id'] not in asset_ids:
                continue

            #: Filter by asset group ID.
            if asset_group_ids:
                a = set(asset_group_ids)
                b = {g['id'] for g in asset['asset_groups']}
                if not a & b:
                    continue

            #: Filter by asset group name.
            if asset_group_names and not hodgepodge.patterns.str_matches_glob(
                values={g['name'] for g in asset['asset_groups']},
                patterns=asset_group_names,
            ):
                continue

            #: Filter by create time.
            if (min_asset_first_seen_time or max_asset_first_seen_time) and \
                    not hodgepodge.time.is_within_range(asset['created_at'], min_asset_first_seen_time, max_asset_first_seen_time):
                continue

            #: Filter by last seen time.
            if (min_asset_last_seen_time or max_asset_last_seen_time) and \
                    not hodgepodge.time.is_within_range(asset['last_seen_time'], min_asset_last_seen_time, max_asset_last_seen_time):
                continue

            #: Filter by last boot time.
            if (min_asset_last_boot_time or max_asset_last_boot_time) and \
                    not hodgepodge.time.is_within_range(asset['last_boot_time'], min_asset_last_boot_time, max_asset_last_boot_time):
                continue

            #: Filter by hostname.
            if asset_hostnames and not hodgepodge.patterns.str_matches_glob(
                values=[hostname for hostname in (asset['hostname'], asset['fqdn']) if hostname],
                patterns=asset_hostnames,
            ):
                continue

            #: Filter by IP address.
            if asset_ip_addresses and not hodgepodge.patterns.str_matches_glob(
                values=[ip for ip in [asset['ip_address'], asset['ipv6']] if ip],
                patterns=asset_ip_addresses,
            ):
                continue

            #: Filter by MAC address.
            if asset_mac_addresses:
                if not asset['mac_address'] or not hodgepodge.patterns.str_matches_glob(
                    values=hodgepodge.network.parse_mac_address(asset['mac_address']),
                    patterns=list(map(hodgepodge.network.parse_mac_address, asset_mac_addresses)),
                ):
                    continue

            #: Filter by tag.
            if asset_tags and not hodgepodge.patterns.str_matches_glob(asset['tags'], asset_tags):
                continue

            #: Filter by risk meter score.
            if (min_asset_risk_meter_score or max_asset_risk_meter_score) and \
                    not hodgepodge.numbers.is_within_range(
                        value=asset['risk_meter_score'],
                        minimum=min_asset_risk_meter_score,
                        maximum=max_asset_risk_meter_score,
                    ):
                continue

            yield asset

            if limit:
                i += 1
                if i >= limit:
                    return

    def get_asset_tags(
            self,
            asset_ids: Optional[Iterable[int]] = None,
            asset_group_ids: Optional[Iterable[int]] = None,
            asset_group_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            asset_hostnames: Optional[Iterable[str]] = None,
            asset_ip_addresses: Optional[Iterable[str]] = None,
            asset_mac_addresses: Optional[Iterable[str]] = None,
            min_asset_risk_meter_score: Optional[int] = None,
            max_asset_risk_meter_score: Optional[int] = None,
            min_asset_first_seen_time: Optional[datetime.datetime] = None,
            max_asset_first_seen_time: Optional[datetime.datetime] = None,
            min_asset_last_seen_time: Optional[datetime.datetime] = None,
            max_asset_last_seen_time: Optional[datetime.datetime] = None,
            min_asset_last_boot_time: Optional[datetime.datetime] = None,
            max_asset_last_boot_time: Optional[datetime.datetime] = None) -> Set[str]:

        return set(self.iter_asset_tags(
            asset_ids=asset_ids,
            asset_group_ids=asset_group_ids,
            asset_group_names=asset_group_names,
            asset_tags=asset_tags,
            asset_hostnames=asset_hostnames,
            asset_ip_addresses=asset_ip_addresses,
            asset_mac_addresses=asset_mac_addresses,
            min_asset_risk_meter_score=min_asset_risk_meter_score,
            max_asset_risk_meter_score=max_asset_risk_meter_score,
            min_asset_first_seen_time=min_asset_first_seen_time,
            max_asset_first_seen_time=max_asset_first_seen_time,
            min_asset_last_seen_time=min_asset_last_seen_time,
            max_asset_last_seen_time=max_asset_last_seen_time,
            min_asset_last_boot_time=min_asset_last_boot_time,
            max_asset_last_boot_time=max_asset_last_boot_time,
        ))

    def iter_asset_tags(
            self,
            asset_ids: Optional[Iterable[int]] = None,
            asset_group_ids: Optional[Iterable[int]] = None,
            asset_group_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            asset_hostnames: Optional[Iterable[str]] = None,
            asset_ip_addresses: Optional[Iterable[str]] = None,
            asset_mac_addresses: Optional[Iterable[str]] = None,
            min_asset_risk_meter_score: Optional[int] = None,
            max_asset_risk_meter_score: Optional[int] = None,
            min_asset_first_seen_time: Optional[datetime.datetime] = None,
            max_asset_first_seen_time: Optional[datetime.datetime] = None,
            min_asset_last_seen_time: Optional[datetime.datetime] = None,
            max_asset_last_seen_time: Optional[datetime.datetime] = None,
            min_asset_last_boot_time: Optional[datetime.datetime] = None,
            max_asset_last_boot_time: Optional[datetime.datetime] = None):

        tags = set()
        for asset in self.iter_assets(
            asset_ids=asset_ids,
            asset_group_ids=asset_group_ids,
            asset_group_names=asset_group_names,
            asset_tags=asset_tags,
            asset_hostnames=asset_hostnames,
            asset_ip_addresses=asset_ip_addresses,
            asset_mac_addresses=asset_mac_addresses,
            min_asset_risk_meter_score=min_asset_risk_meter_score,
            max_asset_risk_meter_score=max_asset_risk_meter_score,
            min_asset_first_seen_time=min_asset_first_seen_time,
            max_asset_first_seen_time=max_asset_first_seen_time,
            min_asset_last_seen_time=min_asset_last_seen_time,
            max_asset_last_seen_time=max_asset_last_seen_time,
            min_asset_last_boot_time=min_asset_last_boot_time,
            max_asset_last_boot_time=max_asset_last_boot_time,
        ):
            for tag in asset['tags']:
                if tag not in tags:
                    tags.add(tag)
                    yield tag

    def get_asset_group(self, asset_group_id: int) -> Optional[dict]:
        url = urllib.parse.urljoin(self.url, '{}/{}'.format(ASSET_GROUPS, asset_group_id))
        return self._get_object(url)

    def get_asset_groups(
            self,
            asset_group_ids: Optional[Iterable[int]] = None,
            asset_group_names: Optional[Iterable[str]] = None,
            asset_ids: Optional[Iterable[int]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            asset_hostnames: Optional[Iterable[str]] = None,
            asset_ip_addresses: Optional[Iterable[str]] = None,
            asset_mac_addresses: Optional[Iterable[str]] = None,
            min_asset_group_create_time: Optional[datetime.datetime] = None,
            max_asset_group_create_time: Optional[datetime.datetime] = None,
            min_asset_group_last_update_time: Optional[datetime.datetime] = None,
            max_asset_group_last_update_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_asset_groups(
            asset_group_ids=asset_group_ids,
            asset_group_names=asset_group_names,
            asset_ids=asset_ids,
            asset_tags=asset_tags,
            asset_hostnames=asset_hostnames,
            asset_ip_addresses=asset_ip_addresses,
            asset_mac_addresses=asset_mac_addresses,
            min_asset_group_create_time=min_asset_group_create_time,
            max_asset_group_create_time=max_asset_group_create_time,
            min_asset_group_last_update_time=min_asset_group_last_update_time,
            max_asset_group_last_update_time=max_asset_group_last_update_time,
            limit=limit,
        ))

    def iter_asset_groups(
            self,
            asset_group_ids: Optional[Iterable[int]] = None,
            asset_group_names: Optional[Iterable[str]] = None,
            asset_ids: Optional[Iterable[int]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            asset_hostnames: Optional[Iterable[str]] = None,
            asset_ip_addresses: Optional[Iterable[str]] = None,
            asset_mac_addresses: Optional[Iterable[str]] = None,
            min_asset_group_create_time: Optional[datetime.datetime] = None,
            max_asset_group_create_time: Optional[datetime.datetime] = None,
            min_asset_group_last_update_time: Optional[datetime.datetime] = None,
            max_asset_group_last_update_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        #: Lookup assets.
        if asset_ids or asset_tags or asset_hostnames or asset_ip_addresses or asset_mac_addresses:
            assets = self.iter_assets(
                asset_ids=asset_ids,
                asset_tags=asset_tags,
                asset_hostnames=asset_hostnames,
                asset_ip_addresses=asset_ip_addresses,
                asset_mac_addresses=asset_mac_addresses,
            )
            asset_group_ids = {g['id'] for g in itertools.chain.from_iterable([a['asset_groups'] for a in assets])}
            asset_group_names = None

        #: Lookup asset groups.
        i = 0
        url = urllib.parse.urljoin(self.url, ASSET_GROUPS)
        for g in self._iter_objects(url=url):

            #: Filter applications by ID.
            if asset_group_ids and g['id'] not in asset_group_ids:
                continue

            #: Filter by asset group name.
            if asset_group_names and not hodgepodge.patterns.str_matches_glob(g['name'], asset_group_names):
                continue

            #: Filter by creation time.
            if (min_asset_group_create_time or max_asset_group_create_time) and \
                    not hodgepodge.time.is_within_range(g['created_at'], min_asset_group_create_time, max_asset_group_create_time):
                continue

            #: Filter by last update time.
            if (min_asset_group_last_update_time or max_asset_group_last_update_time) and \
                    not hodgepodge.time.is_within_range(g['updated_at'], min_asset_group_last_update_time, max_asset_group_last_update_time):
                continue

            yield g

            if limit:
                i += 1
                if i >= limit:
                    return

    def get_connector(self, connector_id: int) -> Optional[dict]:
        url = urllib.parse.urljoin(self.url, '{}/{}'.format(CONNECTORS, connector_id))
        return self._get_object(url)

    def get_connectors(
            self,
            connector_ids: Optional[Iterable[int]] = None,
            connector_names: Optional[Iterable[str]] = None,
            min_connector_run_start_time: Optional[datetime.datetime] = None,
            max_connector_run_start_time: Optional[datetime.datetime] = None,
            min_connector_run_end_time: Optional[datetime.datetime] = None,
            max_connector_run_end_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_connectors(
            connector_ids=connector_ids,
            connector_names=connector_names,
            min_connector_run_start_time=min_connector_run_start_time,
            max_connector_run_start_time=max_connector_run_start_time,
            min_connector_run_end_time=min_connector_run_end_time,
            max_connector_run_end_time=max_connector_run_end_time,
            limit=limit,
        ))

    def iter_connectors(
            self,
            connector_ids: Optional[Iterable[int]] = None,
            connector_names: Optional[Iterable[str]] = None,
            min_connector_run_start_time: Optional[datetime.datetime] = None,
            max_connector_run_start_time: Optional[datetime.datetime] = None,
            min_connector_run_end_time: Optional[datetime.datetime] = None,
            max_connector_run_end_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        #: Lookup connector runs to determine target connector IDs given a min/max start/end time.
        if min_connector_run_start_time or max_connector_run_start_time or min_connector_run_end_time or \
                max_connector_run_end_time:

            runs = self.get_connector_runs_by_connector_id(
                min_connector_run_start_time=min_connector_run_start_time,
                max_connector_run_start_time=max_connector_run_start_time,
                min_connector_run_end_time=min_connector_run_end_time,
                max_connector_run_end_time=max_connector_run_end_time,
            )
            connector_ids = set(runs.keys())

        #: Lookup connector runs.
        i = 0
        url = urllib.parse.urljoin(self.url, CONNECTORS)
        for connector in self._iter_objects(url=url):

            #: Filter by ID.
            if connector_ids and connector['id'] not in connector_ids:
                continue

            #: Filter by name.
            if connector_names and not hodgepodge.patterns.str_matches_glob(connector['name'], connector_names):
                continue

            yield connector

            if limit:
                i += 1
                if i >= limit:
                    return

    def get_connector_run(self, connector_id: int, connector_run_id: int) -> Optional[dict]:
        url = urllib.parse.urljoin(self.url, '{}/{}/{}/{}'.format(CONNECTORS, connector_id, CONNECTOR_RUNS, connector_run_id))
        return self._get_object(url)

    def get_connector_runs_by_connector_id(
            self,
            connector_ids: Optional[Iterable[int]] = None,
            connector_names: Optional[Iterable[str]] = None,
            connector_run_ids: Optional[Iterable[int]] = None,
            min_connector_run_start_time: Optional[datetime.datetime] = None,
            max_connector_run_start_time: Optional[datetime.datetime] = None,
            min_connector_run_end_time: Optional[datetime.datetime] = None,
            max_connector_run_end_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> Dict[int, dict]:

        connector_runs = collections.defaultdict(list)
        i = 0
        for connector in self.iter_connectors(
            connector_ids=connector_ids,
            connector_names=connector_names,
        ):
            url = urllib.parse.urljoin(self.url, '{}/{}/{}'.format(CONNECTORS, connector['id'], CONNECTOR_RUNS))
            for run in self._iter_objects(url=url):

                #: Filter by connector run ID.
                if connector_run_ids and run['id'] not in connector_run_ids:
                    continue

                #: Filter by connector run start time.
                if (min_connector_run_start_time or max_connector_run_start_time) and not \
                        hodgepodge.time.is_within_range(
                            timestamp=run['start_time'],
                            minimum=min_connector_run_start_time,
                            maximum=max_connector_run_start_time,
                        ):
                    continue

                #: Filter by connector run end time.
                if (min_connector_run_end_time or max_connector_run_end_time) and not \
                        hodgepodge.time.is_within_range(
                            timestamp=run['end_time'],
                            minimum=min_connector_run_end_time,
                            maximum=max_connector_run_end_time,
                        ):
                    continue

                connector_runs[connector['id']].append(run)

                if limit:
                    i += 1
                    if i >= limit:
                        return dict(connector_runs)
        return dict(connector_runs)

    def get_dashboard_group(self, dashboard_group_id: int) -> Optional[dict]:
        url = urllib.parse.urljoin(self.url, '{}/{}'.format(DASHBOARD_GROUPS, dashboard_group_id))
        return self._get_object(url)

    def get_dashboard_groups(
            self,
            dashboard_group_ids: Optional[Iterable[int]] = None,
            dashboard_group_names: Optional[Iterable[str]] = None,
            role_ids: Optional[Iterable[int]] = None,
            role_names: Optional[Iterable[str]] = None,
            min_dashboard_group_create_time: Optional[datetime.datetime] = None,
            max_dashboard_group_create_time: Optional[datetime.datetime] = None,
            min_dashboard_group_last_update_time: Optional[datetime.datetime] = None,
            max_dashboard_group_last_update_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_dashboard_groups(
            dashboard_group_ids=dashboard_group_ids,
            dashboard_group_names=dashboard_group_names,
            role_ids=role_ids,
            role_names=role_names,
            min_dashboard_group_create_time=min_dashboard_group_create_time,
            max_dashboard_group_create_time=max_dashboard_group_create_time,
            min_dashboard_group_last_update_time=min_dashboard_group_last_update_time,
            max_dashboard_group_last_update_time=max_dashboard_group_last_update_time,
            limit=limit,
        ))

    def iter_dashboard_groups(
            self,
            dashboard_group_ids: Optional[Iterable[int]] = None,
            dashboard_group_names: Optional[Iterable[str]] = None,
            role_ids: Optional[Iterable[int]] = None,
            role_names: Optional[Iterable[str]] = None,
            min_dashboard_group_create_time: Optional[datetime.datetime] = None,
            max_dashboard_group_create_time: Optional[datetime.datetime] = None,
            min_dashboard_group_last_update_time: Optional[datetime.datetime] = None,
            max_dashboard_group_last_update_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        i = 0
        url = urllib.parse.urljoin(self.url, DASHBOARD_GROUPS)
        for g in self._iter_objects(url=url):

            #: Filter by ID.
            if dashboard_group_ids and g['id'] not in dashboard_group_ids:
                continue

            #: Filter by name.
            if dashboard_group_names and not hodgepodge.patterns.str_matches_glob(g['name'], dashboard_group_names):
                continue

            #: Filter by creation time.
            if (min_dashboard_group_create_time or max_dashboard_group_create_time) and \
                    not hodgepodge.time.is_within_range(g['created_at'], min_dashboard_group_create_time, max_dashboard_group_create_time):
                continue

            #: Filter by last update time.
            if (min_dashboard_group_last_update_time or max_dashboard_group_last_update_time) and \
                    not hodgepodge.time.is_within_range(g['updated_at'], min_dashboard_group_last_update_time, max_dashboard_group_last_update_time):
                continue

            #: Filter by role ID.
            if role_ids:
                a = set(role_ids)
                b = set(g['role_ids'])
                if not (a & b):
                    continue

            #: Filter by role name.
            if role_names:
                a = {role['name'] for role in g['roles']}
                b = set(role_names)
                if not hodgepodge.patterns.str_matches_glob(a, b):
                    continue

            yield g

            if limit:
                i += 1
                if i >= limit:
                    return

    def get_fix(self, fix_id: int) -> Optional[dict]:
        url = urllib.parse.urljoin(self.url, '{}/{}'.format(FIXES, fix_id))
        return self._get_object(url)

    def get_fixes(
            self,
            fix_ids: Optional[Iterable[int]] = None,
            fix_names: Optional[Iterable[str]] = None,
            fix_vendors: Optional[Iterable[str]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            asset_ids: Optional[Iterable[int]] = None,
            asset_hostnames: Optional[Iterable[str]] = None,
            asset_ip_addresses: Optional[Iterable[str]] = None,
            asset_mac_addresses: Optional[Iterable[str]] = None,
            asset_group_ids: Optional[Iterable[int]] = None,
            asset_group_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            min_fix_create_time: Optional[datetime.datetime] = None,
            max_fix_create_time: Optional[datetime.datetime] = None,
            min_fix_last_update_time: Optional[datetime.datetime] = None,
            max_fix_last_update_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_fixes(
            fix_ids=fix_ids,
            fix_names=fix_names,
            fix_vendors=fix_vendors,
            cve_ids=cve_ids,
            asset_ids=asset_ids,
            asset_hostnames=asset_hostnames,
            asset_ip_addresses=asset_ip_addresses,
            asset_mac_addresses=asset_mac_addresses,
            asset_group_ids=asset_group_ids,
            asset_group_names=asset_group_names,
            asset_tags=asset_tags,
            min_fix_create_time=min_fix_create_time,
            max_fix_create_time=max_fix_create_time,
            min_fix_last_update_time=min_fix_last_update_time,
            max_fix_last_update_time=max_fix_last_update_time,
            limit=limit,
        ))

    def iter_fixes(
            self,
            fix_ids: Optional[Iterable[int]] = None,
            fix_names: Optional[Iterable[str]] = None,
            fix_vendors: Optional[Iterable[str]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            asset_ids: Optional[Iterable[int]] = None,
            asset_hostnames: Optional[Iterable[str]] = None,
            asset_ip_addresses: Optional[Iterable[str]] = None,
            asset_mac_addresses: Optional[Iterable[str]] = None,
            asset_group_ids: Optional[Iterable[int]] = None,
            asset_group_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            min_fix_create_time: Optional[datetime.datetime] = None,
            max_fix_create_time: Optional[datetime.datetime] = None,
            min_fix_last_update_time: Optional[datetime.datetime] = None,
            max_fix_last_update_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        #: Lookup assets.
        if any((asset_ids, asset_group_ids, asset_hostnames, asset_ip_addresses, asset_mac_addresses, asset_group_ids,
                asset_group_names, asset_tags)):

            assets = self.iter_assets(
                asset_ids=asset_ids,
                asset_group_ids=asset_group_ids,
                asset_group_names=asset_group_names,
                asset_tags=asset_tags,
                asset_hostnames=asset_hostnames,
                asset_ip_addresses=asset_ip_addresses,
                asset_mac_addresses=asset_mac_addresses,
            )
            asset_ids = {asset['id'] for asset in assets}

        #: Lookup fixes.
        i = 0
        url = urllib.parse.urljoin(self.url, FIXES)
        for fix in self._iter_objects(url=url):

            #: Filter by ID.
            if fix_ids and fix['id'] not in fix_ids:
                continue

            #: Filter by asset ID.
            if asset_ids:
                a = {asset['id'] for asset in fix['assets']}
                b = set(asset_ids)
                if not (a & b):
                    continue

            #: Filter by name.
            if fix_names and not hodgepodge.patterns.str_matches_glob(fix['title'], fix_names):
                continue

            #: Filter by vendor name.
            if fix_vendors and not hodgepodge.patterns.str_matches_glob(fix['vendor'], fix_vendors):
                continue

            #: Filter by CVE ID.
            if cve_ids:
                a = set(fix['cves'])
                b = set(cve_ids)
                if not (a & b):
                    continue

            #: Filter by creation time.
            if min_fix_create_time or max_fix_create_time:
                if not hodgepodge.time.is_within_range(
                    timestamp=fix['patch_publication_date'],
                    minimum=min_fix_create_time,
                    maximum=max_fix_create_time,
                ):
                    continue

            #: Filter by last update time.
            if min_fix_last_update_time or max_fix_last_update_time:
                if not hodgepodge.time.is_within_range(
                    timestamp=fix['updated_at'],
                    minimum=min_fix_last_update_time,
                    maximum=max_fix_last_update_time,
                ):
                    continue

            yield fix

            if limit:
                i += 1
                if i >= limit:
                    return

    def get_vulnerability(self, vulnerability_id: int) -> Optional[dict]:
        url = urllib.parse.urljoin(self.url, '{}/{}'.format(VULNERABILITIES, vulnerability_id))
        return self._get_object(url)

    def get_vulnerabilities(
            self,
            vulnerability_ids: Optional[Iterable[int]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            fix_ids: Optional[Iterable[int]] = None,
            fix_names: Optional[Iterable[str]] = None,
            fix_vendors: Optional[Iterable[str]] = None,
            asset_ids: Optional[Iterable[int]] = None,
            asset_hostnames: Optional[Iterable[str]] = None,
            asset_ip_addresses: Optional[Iterable[str]] = None,
            asset_mac_addresses: Optional[Iterable[str]] = None,
            asset_group_ids: Optional[Iterable[int]] = None,
            asset_group_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            min_vulnerability_risk_meter_score: Optional[int] = None,
            max_vulnerability_risk_meter_score: Optional[int] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_first_seen_time: Optional[datetime.datetime] = None,
            max_vulnerability_first_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_last_seen_time: Optional[datetime.datetime] = None,
            max_vulnerability_last_seen_time: Optional[datetime.datetime] = None,
            min_cve_publish_time: Optional[datetime.datetime] = None,
            max_cve_publish_time: Optional[datetime.datetime] = None,
            min_patch_publish_time: Optional[datetime.datetime] = None,
            max_patch_publish_time: Optional[datetime.datetime] = None,
            min_patch_due_date: Optional[datetime.date] = None,
            max_patch_due_date: Optional[datetime.date] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_vulnerabilities(
            vulnerability_ids=vulnerability_ids,
            cve_ids=cve_ids,
            fix_ids=fix_ids,
            fix_names=fix_names,
            fix_vendors=fix_vendors,
            asset_ids=asset_ids,
            asset_hostnames=asset_hostnames,
            asset_ip_addresses=asset_ip_addresses,
            asset_mac_addresses=asset_mac_addresses,
            asset_group_ids=asset_group_ids,
            asset_group_names=asset_group_names,
            asset_tags=asset_tags,
            min_vulnerability_risk_meter_score=min_vulnerability_risk_meter_score,
            max_vulnerability_risk_meter_score=max_vulnerability_risk_meter_score,
            min_vulnerability_create_time=min_vulnerability_create_time,
            max_vulnerability_create_time=max_vulnerability_create_time,
            min_vulnerability_first_seen_time=min_vulnerability_first_seen_time,
            max_vulnerability_first_seen_time=max_vulnerability_first_seen_time,
            min_vulnerability_last_seen_time=min_vulnerability_last_seen_time,
            max_vulnerability_last_seen_time=max_vulnerability_last_seen_time,
            min_cve_publish_time=min_cve_publish_time,
            max_cve_publish_time=max_cve_publish_time,
            min_patch_publish_time=min_patch_publish_time,
            max_patch_publish_time=max_patch_publish_time,
            min_patch_due_date=min_patch_due_date,
            max_patch_due_date=max_patch_due_date,
            limit=limit,
        ))

    def iter_vulnerabilities(
            self,
            vulnerability_ids: Optional[Iterable[int]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            fix_ids: Optional[Iterable[int]] = None,
            fix_names: Optional[Iterable[str]] = None,
            fix_vendors: Optional[Iterable[str]] = None,
            asset_ids: Optional[Iterable[str]] = None,
            asset_hostnames: Optional[Iterable[str]] = None,
            asset_ip_addresses: Optional[Iterable[str]] = None,
            asset_mac_addresses: Optional[Iterable[str]] = None,
            asset_group_ids: Optional[Iterable[str]] = None,
            asset_group_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            min_vulnerability_risk_meter_score: Optional[int] = None,
            max_vulnerability_risk_meter_score: Optional[int] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_first_seen_time: Optional[datetime.datetime] = None,
            max_vulnerability_first_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_last_seen_time: Optional[datetime.datetime] = None,
            max_vulnerability_last_seen_time: Optional[datetime.datetime] = None,
            min_cve_publish_time: Optional[datetime.datetime] = None,
            max_cve_publish_time: Optional[datetime.datetime] = None,
            min_patch_publish_time: Optional[datetime.datetime] = None,
            max_patch_publish_time: Optional[datetime.datetime] = None,
            min_patch_due_date: Optional[datetime.date] = None,
            max_patch_due_date: Optional[datetime.date] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        #: Lookup assets.
        if asset_ids or asset_group_ids or asset_hostnames or asset_ip_addresses or asset_mac_addresses or \
                asset_group_ids or asset_group_names or asset_tags:

            assets = self.iter_assets(
                asset_ids=asset_ids,
                asset_group_ids=asset_group_ids,
                asset_group_names=asset_group_names,
                asset_hostnames=asset_hostnames,
                asset_ip_addresses=asset_ip_addresses,
                asset_mac_addresses=asset_mac_addresses,
                asset_tags=asset_tags,
            )
            asset_ids = {asset['id'] for asset in assets}

        #: Lookup fixes.
        if fix_ids or fix_names or fix_vendors:
            fixes = self.iter_fixes(
                fix_ids=fix_ids,
                fix_names=fix_names,
                fix_vendors=fix_vendors,
            )
            fix_ids = {fix['id'] for fix in fixes}

        #: Lookup vulnerabilities.
        i = 0
        url = urllib.parse.urljoin(self.url, '{}'.format(VULNERABILITIES))
        for vulnerability in self._iter_objects(url=url):

            #: Filter by vulnerability ID.
            if vulnerability_ids and vulnerability['id'] not in vulnerability_ids:
                continue

            #: Filter by asset ID.
            if asset_ids and vulnerability['asset_id'] not in asset_ids:
                continue

            #: Filter by fix ID.
            if fix_ids and vulnerability['fix_id'] not in fix_ids:
                continue

            #: Filter by CVE ID.
            if cve_ids and vulnerability['cve_id'] not in cve_ids:
                continue

            #: Filter by risk meter score.
            if (min_vulnerability_risk_meter_score or max_vulnerability_risk_meter_score) and not hodgepodge.numbers.is_within_range(
                value=vulnerability['risk_meter_score'],
                minimum=min_vulnerability_risk_meter_score,
                maximum=max_vulnerability_risk_meter_score,
            ):
                continue

            #: Filter by create time.
            if (min_vulnerability_create_time or max_vulnerability_create_time) and not hodgepodge.time.is_within_range(
                timestamp=vulnerability['created_at'],
                minimum=min_vulnerability_create_time,
                maximum=max_vulnerability_create_time,
            ):
                continue

            #: Filter by first seen time.
            if (min_vulnerability_first_seen_time or max_vulnerability_first_seen_time) and not hodgepodge.time.is_within_range(
                timestamp=vulnerability['first_found_on'],
                minimum=min_vulnerability_first_seen_time,
                maximum=max_vulnerability_first_seen_time,
            ):
                continue

            #: Filter by last seen time.
            if (min_vulnerability_last_seen_time or max_vulnerability_last_seen_time) and not hodgepodge.time.is_within_range(
                timestamp=vulnerability['last_seen_time'],
                minimum=min_vulnerability_last_seen_time,
                maximum=max_vulnerability_last_seen_time,
            ):
                continue

            #: Filter by CVE publish time.
            if (min_cve_publish_time or max_cve_publish_time) and not hodgepodge.time.is_within_range(
                timestamp=vulnerability['cve_published_at'],
                minimum=min_cve_publish_time,
                maximum=max_cve_publish_time,
            ):
                continue

            #: Filter by patch publish time.
            if (min_patch_publish_time or max_patch_publish_time) and not hodgepodge.time.is_within_range(
                timestamp=vulnerability['patch_published_at'],
                minimum=min_patch_publish_time,
                maximum=max_patch_publish_time,
            ):
                continue

            #: Filter by patch due date.
            if (min_patch_due_date or max_patch_due_date) and not hodgepodge.time.is_within_range(
                timestamp=vulnerability['due_date'],
                minimum=min_patch_due_date,
                maximum=max_patch_due_date,
            ):
                continue

            yield vulnerability

            if limit:
                i += 1
                if i >= limit:
                    return

    def get_user(self, user_id: int):
        url = urllib.parse.urljoin(self.url, '{}/{}'.format(USERS, user_id))
        return self._get_object(url)

    def get_users(
            self,
            user_ids: Optional[Iterable[int]] = None,
            user_names: Optional[Iterable[str]] = None,
            user_email_addresses: Optional[Iterable[str]] = None,
            role_ids: Optional[Iterable[int]] = None,
            role_names: Optional[Iterable[str]] = None,
            min_user_create_time: Optional[datetime.datetime] = None,
            max_user_create_time: Optional[datetime.datetime] = None,
            min_user_last_update_time: Optional[datetime.datetime] = None,
            max_user_last_update_time: Optional[datetime.datetime] = None,
            min_user_last_sign_in_time: Optional[datetime.datetime] = None,
            max_user_last_sign_in_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_users(
            user_ids=user_ids,
            user_names=user_names,
            user_email_addresses=user_email_addresses,
            role_ids=role_ids,
            role_names=role_names,
            min_user_create_time=min_user_create_time,
            max_user_create_time=max_user_create_time,
            min_user_last_update_time=min_user_last_update_time,
            max_user_last_update_time=max_user_last_update_time,
            min_user_last_sign_in_time=min_user_last_sign_in_time,
            max_user_last_sign_in_time=max_user_last_sign_in_time,
            limit=limit,
        ))

    def iter_users(
            self,
            user_ids: Optional[Iterable[int]] = None,
            user_names: Optional[Iterable[str]] = None,
            user_email_addresses: Optional[Iterable[str]] = None,
            role_ids: Optional[Iterable[int]] = None,
            role_names: Optional[Iterable[str]] = None,
            min_user_create_time: Optional[datetime.datetime] = None,
            max_user_create_time: Optional[datetime.datetime] = None,
            min_user_last_update_time: Optional[datetime.datetime] = None,
            max_user_last_update_time: Optional[datetime.datetime] = None,
            min_user_last_sign_in_time: Optional[datetime.datetime] = None,
            max_user_last_sign_in_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        i = 0
        url = urllib.parse.urljoin(self.url, USERS)
        for user in self._iter_objects(url):

            #: Filter by ID.
            if user_ids and user['id'] not in user_ids:
                continue

            #: Filter by creation time.
            if (min_user_create_time or max_user_create_time) and not hodgepodge.time.is_within_range(
                timestamp=user['created_at'],
                minimum=min_user_create_time,
                maximum=max_user_create_time,
            ):
                continue

            #: Filter by last update time.
            if (min_user_last_update_time or max_user_last_update_time) and not hodgepodge.time.is_within_range(
                timestamp=user['updated_at'],
                minimum=min_user_last_update_time,
                maximum=max_user_last_update_time,
            ):
                continue

            #: Filter by last sign-in time.
            if (min_user_last_sign_in_time or max_user_last_sign_in_time) and not hodgepodge.time.is_within_range(
                timestamp=user['last_sign_in_at'],
                minimum=min_user_last_sign_in_time,
                maximum=max_user_last_sign_in_time,
            ):
                continue

            #: Filter by name.
            if user_names:
                values = {
                    user['firstname'],
                    user['lastname'],
                    user['firstname'] + ' ' + user['lastname'],
                    user['external_id'],
                    user['email'],
                }
                if not hodgepodge.patterns.str_matches_glob(values, user_names):
                    continue

            #: Filter by email address.
            if user_email_addresses and not hodgepodge.patterns.str_matches_glob(user['email'], user_email_addresses):
                continue

            #: Filter by role ID.
            if role_ids:
                a = set(role_ids)
                b = set(user['role_ids'])
                if not (a & b):
                    continue

            #: Filter by role name.
            if role_names and not hodgepodge.patterns.str_matches_glob(user['roles'], role_names):
                continue

            yield user

            if limit:
                i += 1
                if i >= limit:
                    return

    def get_role(self, role_id: int) -> Optional[dict]:
        url = urllib.parse.urljoin(self.url, '{}/{}'.format(ROLES, role_id))
        return self._get_object(url)

    def get_roles(
            self,
            role_ids: Optional[Iterable[int]] = None,
            role_names: Optional[Iterable[str]] = None,
            role_types: Optional[Iterable[str]] = None,
            role_access_levels: Optional[Iterable[str]] = None,
            role_custom_permissions: Optional[Iterable[str]] = None,
            user_ids: Optional[Iterable[int]] = None,
            user_email_addresses: Optional[Iterable[str]] = None,
            user_names: Optional[Iterable[str]] = None,
            min_role_create_time: Optional[datetime.datetime] = None,
            max_role_create_time: Optional[datetime.datetime] = None,
            min_role_last_update_time: Optional[datetime.datetime] = None,
            max_role_last_update_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_roles(
            role_ids=role_ids,
            role_names=role_names,
            role_types=role_types,
            role_access_levels=role_access_levels,
            role_custom_permissions=role_custom_permissions,
            user_ids=user_ids,
            user_email_addresses=user_email_addresses,
            user_names=user_names,
            min_role_create_time=min_role_create_time,
            max_role_create_time=max_role_create_time,
            min_role_last_update_time=min_role_last_update_time,
            max_role_last_update_time=max_role_last_update_time,
            limit=limit,
        ))

    def iter_roles(
            self,
            role_ids: Optional[Iterable[int]] = None,
            role_names: Optional[Iterable[str]] = None,
            role_types: Optional[Iterable[str]] = None,
            role_access_levels: Optional[Iterable[str]] = None,
            role_custom_permissions: Optional[Iterable[str]] = None,
            user_ids: Optional[Iterable[int]] = None,
            user_email_addresses: Optional[Iterable[str]] = None,
            user_names: Optional[Iterable[str]] = None,
            min_role_create_time: Optional[datetime.datetime] = None,
            max_role_create_time: Optional[datetime.datetime] = None,
            min_role_last_update_time: Optional[datetime.datetime] = None,
            max_role_last_update_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        #: Lookup users.
        if user_ids or user_names:
            users = self.iter_users(
                user_ids=user_ids,
                user_email_addresses=user_email_addresses,
                user_names=user_names
            )
            role_ids = set(itertools.chain.from_iterable(user['role_ids'] for user in users))

        #: Lookup roles.
        i = 0
        url = urllib.parse.urljoin(self.url, ROLES)
        for role in self._iter_objects(url):

            #: Filter by ID.
            if role_ids and role['id'] not in role_ids:
                continue

            #: Filter by name.
            if role_names and not hodgepodge.patterns.str_matches_glob(role['name'], role_names):
                continue

            #: Filter by type.
            if role_types and not hodgepodge.patterns.str_matches_glob(role['role_type'], role_types):
                continue

            #: Filter by access level.
            if role_access_levels and not hodgepodge.patterns.str_matches_glob(role['access_level'], role_access_levels):
                continue

            #: Filter by permission name.
            if role_custom_permissions and not hodgepodge.patterns.str_matches_glob(role['custom_permissions'], role_custom_permissions):
                continue

            #: Filter by creation time.
            if (min_role_create_time or max_role_create_time) and not hodgepodge.time.is_within_range(
                timestamp=role['created_at'],
                minimum=min_role_create_time,
                maximum=max_role_create_time,
            ):
                continue

            #: Filter by last update time.
            if (min_role_last_update_time or max_role_last_update_time) and not hodgepodge.time.is_within_range(
                timestamp=role['updated_at'],
                minimum=min_role_last_update_time,
                maximum=max_role_last_update_time,
            ):
                continue

            yield role

            if limit:
                i += 1
                if i >= limit:
                    return

    def get_business_units(
            self,
            application_ids: Optional[Optional[Iterable[str]]],
            application_names: Optional[Optional[Iterable[str]]] = None) -> List[dict]:

        apps = self.iter_applications(
            application_ids=application_ids,
            application_names=application_names,
        )
        names = {app['business_units'] for app in apps if app['business_units']}
        units = [{'name': name} for name in names]
        return units

    def get_teams(
            self,
            application_ids: Optional[Optional[Iterable[str]]],
            application_names: Optional[Optional[Iterable[str]]] = None) -> List[dict]:

        apps = self.iter_applications(
            application_ids=application_ids,
            application_names=application_names,
        )
        names = {app['team_name'] for app in apps if app['team_name']}
        teams = [{'name': name} for name in names]
        return teams
