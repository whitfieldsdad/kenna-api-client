from typing import Optional, Iterator, Iterable, List, Set, Tuple, Dict
from kenna.constants import MAX_PAGES_ALLOWED_BY_API, DATA_EXPORT_TYPES, DEFAULT_ACCESS_LEVEL, \
    COLLECTION_TYPES_TO_OBJECT_TYPES, OBJECT_TYPES_TO_COLLECTION_TYPES, COLLECTION_TYPES, OBJECT_TYPES

from kenna.errors import NotFoundError, WriteError
from kenna.region import DEFAULT_REGION
from kenna.authentication import DEFAULT_API_KEY
from kenna.types.data_export_status import DataExportStatus
from hodgepodge.http import DEFAULT_MAX_RETRIES_ON_REDIRECT, DEFAULT_MAX_RETRIES_ON_CONNECTION_ERRORS, \
    DEFAULT_MAX_RETRIES_ON_READ_ERRORS, DEFAULT_BACKOFF_FACTOR

import datetime
import concurrent.futures
import hodgepodge.archiving
import hodgepodge.compression
import hodgepodge.files
import hodgepodge.hashing
import hodgepodge.networking
import hodgepodge.math
import hodgepodge.pattern_matching
import hodgepodge.http
import hodgepodge.time
import hodgepodge.types
import hodgepodge.web
import hodgepodge.uuid
import itertools
import kenna.authentication
import concurrent.futures
import kenna.helpers
import kenna.region
import logging
import requests
import urllib.parse
import collections
import threading
import gzip
import copy
import json

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

JOURNAL_FILENAME = 'journal.db'


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
        self.session.headers.update({
            'X-Risk-Token': kenna.authentication.validate_api_key(api_key),
            'Content-Type': 'application/json'
        })
        auto_retry_policy = hodgepodge.http.get_automatic_retry_policy(
            max_retries_on_connection_errors=max_retries_on_connection_errors,
            max_retries_on_read_errors=max_retries_on_read_errors,
            max_retries_on_redirects=max_retries_on_redirects,
            backoff_factor=backoff_factor,
        )
        hodgepodge.http.attach_session_policies(session=self.session, policies=[auto_retry_policy])

    def _get(self, url: str, params: Optional[dict] = None, stream: bool = False) -> requests.Response:
        logger.info("Sending HTTP GET request: %s", url)
        response = self.session.get(url, params=params, stream=stream)
        request = response.request
        logger.info("Received HTTP GET response: %s (status code: %d)", request.url, response.status_code)
        return response

    def _post(self, url: str, data: dict) -> requests.Response:
        logger.info("Sending HTTP POST request: %s (data: %s)", url, data)
        response = self.session.post(url=url, json=data)
        request = response.request
        logger.info("Received HTTP POST response: %s (data: %s, status code: %d)", request.url, data, response.status_code)
        return response

    def _put(self, url: str, data: dict) -> requests.Response:
        logger.info("Sending HTTP PUT request: %s (data: %s)", url, data)
        response = self.session.put(url=url, data=data)
        request = response.request
        logger.info("Received HTTP PUT response: %s (data: %s, status code: %d)", request.url, response.status_code)
        return response

    def _delete(self, url: str, data: Optional[dict] = None) -> requests.Response:
        data = data or None
        logger.info("Sending HTTP DELETE request: %s (data: %s)", url, data)
        response = self.session.delete(url=url, data=data)
        request = response.request
        logger.info("Received HTTP DELETE response: %s (data: %s, status code: %d)",
                    request.url, data, response.status_code)
        return response

    def _get_object(self, url: str) -> Optional[dict]:
        response = self._get(url)
        if response.status_code == 404:
            return None
        else:
            reply = response.json()
            for object_type in OBJECT_TYPES:
                if object_type in reply:
                    return reply[object_type]
            return reply

    def _get_object_by_id(self, object_type: str, object_id: int) -> Optional[dict]:
        url = urllib.parse.urljoin(self.url, '{}/{}'.format(object_type, object_id))
        return self._get_object(url)

    def _iter_objects(self, url: str, page_size: int = 500, limit: Optional[int] = None) -> Iterator[dict]:
        object_type = _get_object_type_from_url(url)
        if self._data_export_is_required(object_type=object_type, limit=limit):
            stream = self._iter_objects_via_asynchronous_api(
                object_type=object_type,
                limit=limit
            )
        else:
            stream = self._iter_objects_via_synchronous_api(
                url=url,
                page_size=page_size,
                limit=limit,
            )

        for row in stream:
            yield row

    def _iter_objects_via_synchronous_api(
            self,
            url: str,
            page_size: int = 500,
            limit: Optional[int] = None) -> Iterator[dict]:

        params = {
            'per_page': page_size,
        }
        response = self._get(url, params=params)
        data = response.json()

        #: If the response is not paginated.
        if isinstance(data, list):
            if limit:
                data = list(itertools.islice(iter(data), limit))
            for row in data:
                yield row
            return

        #: Read the first page of the response.
        collection_type = next(collection_type for collection_type in COLLECTION_TYPES if collection_type in data)
        total = 0
        for row in data[collection_type]:
            yield row

            total += 1
            if limit and total >= limit:
                return

        #: Read any remaining response pages.
        meta = data.get('meta')
        if meta:
            for page_number in range(2, min(meta['pages'] + 1, MAX_PAGES_ALLOWED_BY_API)):
                response = self._get(url, params={'page': page_number})
                data = response.json()
                for row in data[collection_type]:
                    yield row

                    total += 1
                    if limit and total >= limit:
                        return

    def _iter_objects_via_asynchronous_api(self, object_type: str, limit: Optional[int] = None) -> Iterator[dict]:
        export_type = kenna.helpers.object_type_to_data_export_type(object_type)
        search_id = self.request_data_export(export_type)

        rows = self.iter_data_export_response(search_id)
        if limit:
            rows = itertools.islice(rows, limit)
        return rows

    def _delete_object(self, object_type: str, object_id: int):
        object_type = object_type if object_type in COLLECTION_TYPES else OBJECT_TYPES_TO_COLLECTION_TYPES[object_type]
        url = urllib.parse.urljoin(self.url, '{}/{}'.format(object_type, object_id))
        return self._delete(url)

    def _delete_objects(self, object_type: str, object_ids: Iterable[int]):
        futures = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for object_id in object_ids:
                future = executor.submit(self._delete_object, object_type=object_type, object_id=object_id)
                futures.append(future)
            concurrent.futures.wait(futures)

    def _data_export_is_required(self, object_type: str, limit: Optional[int] = None) -> bool:
        if object_type in ['asset', 'vulnerability', 'fix']:
            if limit is not None and limit < 10000:
                return False

            collection_type = OBJECT_TYPES_TO_COLLECTION_TYPES[object_type]
            url = urllib.parse.urljoin(self.url, collection_type)
            response = self._get(url)
            data = response.json()

            return data['meta']['pages'] > 20
        return False

    def request_data_export(self, export_type: str) -> int:
        logger.info("Requesting %s data export", export_type)
        if export_type not in DATA_EXPORT_TYPES:
            raise ValueError(export_type)

        url = urllib.parse.urljoin(self.url, 'data_exports')
        data = {
            'export_settings': {
                'model': export_type,
                'format': 'json',
            }
        }
        response = self._post(url, data=data)
        data = response.json()
        search_id = data['search_id']
        logger.info("Requested %s data export (search ID: %d)", export_type, search_id)
        return search_id

    def iter_data_export_response(self, search_id: int) -> Iterator[dict]:
        self.wait_for_data_export(search_id)

        #: Download the export.
        logger.info("Downloading data export (search ID: %d)", search_id)
        url = urllib.parse.urljoin(self.url, 'data_exports?search_id={}'.format(search_id))
        response = self.session.get(url=url, stream=True)

        #: Note: this deserialization method only works for JSON - not JSONL or XML.
        data = json.loads(gzip.decompress(response.raw.read()))
        collection_type = next(t for t in COLLECTION_TYPES if t in data)
        for row in data[collection_type]:
            yield row

    def get_data_export_status(self, search_id: int) -> Optional[DataExportStatus]:
        url = urllib.parse.urljoin(self.url, 'data_exports/status?search_id={}'.format(search_id))
        response = self._get(url)

        code = response.status_code
        if code == 200:
            return DataExportStatus(search_id=search_id, status='done')
        elif code == 206:
            return DataExportStatus(search_id=search_id, status='running')
        elif code == 404:
            raise NotFoundError("Unknown data export: %s", search_id)

    def wait_for_data_export(self, search_id: int):
        return self.wait_for_data_exports([search_id])

    def wait_for_data_exports(self, search_ids: Iterable[int]):
        search_ids = collections.deque(search_ids)

        shutdown_event = threading.Event()
        logger.info("Waiting for %d data exports to complete (search IDs: %s)",
                    len(search_ids), ','.join(map(str, sorted(search_ids))))

        while search_ids and not shutdown_event.is_set():
            for search_id in copy.copy(search_ids):
                export = self.get_data_export_status(search_id)
                if export.is_done():
                    logger.info("Data export has completed: %d", search_id)
                    search_ids.remove(search_id)

            shutdown_event.wait(0.5)

    def delete_applications(self, application_ids: Iterable[int]):
        return self._delete_objects('applications', application_ids)

    def delete_users(self, user_ids: Iterable[int]):
        return self._delete_objects('users', user_ids)

    def delete_roles(self, role_ids: Iterable[int]):
        return self._delete_objects('roles', role_ids)

    def delete_asset_groups(self, asset_group_ids: Iterable[int]):
        return self._delete_objects('asset_groups', asset_group_ids)

    def delete_dashboard_groups(self, dashboard_group_ids: Iterable[int]):
        return self._delete_objects('dashboard_groups', dashboard_group_ids)

    def delete_vulnerabilities(self, vulnerability_ids: Iterable[int]):
        url = urllib.parse.urljoin(self.url, 'vulnerabilities/bulk_delete')
        futures = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for chunk in hodgepodge.types.iterate_in_chunks(vulnerability_ids, chunk_size=2000):
                future = executor.submit(self._delete, url=url, json={'vulnerability_ids': chunk})
                futures.append(future)
            concurrent.futures.wait(futures)

    def get_application(self, application_id: int) -> Optional[dict]:
        return self._get_object_by_id('applications', application_id)

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

        url = urllib.parse.urljoin(self.url, 'applications')
        apps = self._iter_objects(url, limit=limit)
        apps = self.filter_applications(
            applications=apps,
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
        )
        if limit:
            apps = itertools.islice(apps, limit)
        return apps

    def filter_applications(
            self,
            applications: Iterable[dict],
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
            max_vulnerability_count: Optional[int] = None) -> Iterator[dict]:

        for app in applications:

            #: Filter applications by ID.
            if application_ids and app['id'] not in application_ids:
                continue

            #: Filter applications by name.
            if application_names:
                if not hodgepodge.pattern_matching.str_matches_glob(app['name'], application_names):
                    continue

            #: Filter applications by by owner.
            if application_owners:
                if not hodgepodge.pattern_matching.str_matches_glob(app['owner'], application_owners):
                    continue

            #: Filter applications by team name.
            if application_teams:
                if not hodgepodge.pattern_matching.str_matches_glob(app['team_name'], application_teams):
                    continue

            #: Filter application by business unit.
            if application_business_units:
                if not hodgepodge.pattern_matching.str_matches_glob(app['business_units'], application_business_units):
                    continue

            #: Filter applications by meter score.
            if (min_application_risk_meter_score or max_application_risk_meter_score) is not None:
                if not hodgepodge.math.in_range(
                    value=app['risk_meter_score'],
                    minimum=min_application_risk_meter_score,
                    maximum=max_application_risk_meter_score,
                ):
                    continue

            #: Filter applications by vulnerability count.
            if (min_vulnerability_count or max_vulnerability_count) is not None:
                if not hodgepodge.math.in_range(
                    value=app['total_vulnerability_count'],
                    minimum=min_vulnerability_count,
                    maximum=max_vulnerability_count,
                ):
                    continue

            #: Filter applications by asset count.
            if (min_asset_count or max_asset_count) is not None:
                if not hodgepodge.math.in_range(
                    value=app['asset_count'],
                    minimum=min_asset_count,
                    maximum=max_asset_count,
                ):
                    continue

            yield app

    def count_applications(
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
            max_vulnerability_count: Optional[int] = None) -> int:

        applications = self.iter_applications(
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
        )
        return sum(1 for _ in applications)

    def get_asset(self, asset_id: int) -> Optional[dict]:
        url = urllib.parse.urljoin(self.url, 'assets/{}'.format(asset_id))
        return self._get_object(url)

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

        url = urllib.parse.urljoin(self.url, 'assets')
        assets = self._iter_objects(url, limit=limit)
        assets = self.filter_assets(
            assets=assets,
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
        )
        if limit:
            assets = itertools.islice(assets, limit)
        return assets

    def count_assets(
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
            max_asset_last_boot_time: Optional[datetime.datetime] = None) -> int:

        assets = self.iter_assets(
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
        )
        return sum(1 for _ in assets)

    def filter_assets(
            self,
            assets: Iterable[dict],
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

        for asset in assets:

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
            if asset_group_names:
                names = {g['name'] for g in asset['asset_groups']}
                if (not names) or (not hodgepodge.pattern_matching.str_matches_glob(names, asset_group_names)):
                    continue

            #: Filter by create time.
            if min_asset_first_seen_time or max_asset_first_seen_time:
                if not hodgepodge.time.in_range(
                    timestamp=asset['created_at'],
                    minimum=min_asset_first_seen_time,
                    maximum=max_asset_first_seen_time,
                ):
                    continue

            #: Filter by last seen time.
            if min_asset_last_seen_time or max_asset_last_seen_time:
                if not hodgepodge.time.in_range(
                    timestamp=asset['last_seen_time'],
                    minimum=min_asset_last_seen_time,
                    maximum=max_asset_last_seen_time,
                ):
                    continue

            #: Filter by last boot time.
            if min_asset_last_boot_time or max_asset_last_boot_time:
                if not hodgepodge.time.in_range(
                    timestamp=asset['last_boot_time'],
                    minimum=min_asset_last_boot_time,
                    maximum=max_asset_last_boot_time,
                ):
                    continue

            #: Filter by hostname.
            if asset_hostnames and not hodgepodge.pattern_matching.str_matches_glob(
                values=[hostname for hostname in (asset['hostname'], asset['fqdn']) if hostname],
                patterns=asset_hostnames,
            ):
                continue

            #: Filter by IP address.
            if asset_ip_addresses and not hodgepodge.pattern_matching.str_matches_glob(
                values=[ip for ip in [asset['ip_address'], asset['ipv6']] if ip],
                patterns=asset_ip_addresses,
            ):
                continue

            #: Filter by MAC address.
            if asset_mac_addresses:
                if not asset['mac_address'] or not hodgepodge.pattern_matching.str_matches_glob(
                    values=hodgepodge.networking.parse_mac_address(asset['mac_address']),
                    patterns=list(map(hodgepodge.networking.parse_mac_address, asset_mac_addresses)),
                ):
                    continue

            #: Filter by tag.
            if asset_tags and not hodgepodge.pattern_matching.str_matches_glob(asset['tags'], asset_tags):
                continue

            #: Filter by risk meter score.
            if min_asset_risk_meter_score or max_asset_risk_meter_score:
                if not hodgepodge.math.in_range(
                    value=asset['risk_meter_score'],
                    minimum=min_asset_risk_meter_score,
                    maximum=max_asset_risk_meter_score,
                ):
                    continue

            yield asset

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
        return tags

    def tag_assets(self, asset_ids: Iterable[int], tags: Iterable[str]):
        self.update_assets(asset_ids=asset_ids, tags_to_add=set(tags))

    def untag_assets(self, asset_ids: Iterable[int], tags: Optional[Iterable[str]] = None):
        if tags:
            self.update_assets(asset_ids=asset_ids, tags_to_remove=set(tags))
        else:
            self.update_assets(asset_ids=asset_ids, reset_tags=True)

    def reset_asset_tags(self, asset_ids: Iterable[int]):
        return self.untag_assets(asset_ids)

    def update_assets(
            self,
            asset_ids: Iterable[int],
            tags_to_add: Optional[Iterable[str]] = None,
            tags_to_remove: Optional[Iterable[str]] = None,
            reset_tags: Optional[bool] = None):

        url = urllib.parse.urljoin(self.url, 'assets/bulk')
        data = {
            'asset_ids': asset_ids,
            'asset': {}
        }

        #: Tags to add if not present.
        if tags_to_add:
            data['asset']['tags'] = list(tags_to_add)

        #: Tags to remove if present.
        if tags_to_remove:
            data['asset']['remove_tags'] = list(tags_to_remove)

        #: To remove all asset tags.
        if reset_tags:
            data['asset']['reset_tags'] = True

        if not data['asset']:
            return

        self._put(url=url, data=data)

    def get_asset_group(self, asset_group_id: int) -> Optional[dict]:
        return self._get_object_by_id('asset_groups', asset_group_id)

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

        #: Lookup and filter asset groups.
        url = urllib.parse.urljoin(self.url, 'asset_groups')
        asset_groups = self._iter_objects(url, limit=limit)
        asset_groups = self.filter_asset_groups(
            asset_groups=asset_groups,
            asset_group_ids=asset_group_ids,
            asset_group_names=asset_group_names,
            min_asset_group_create_time=min_asset_group_create_time,
            max_asset_group_create_time=max_asset_group_create_time,
            min_asset_group_last_update_time=min_asset_group_last_update_time,
            max_asset_group_last_update_time=max_asset_group_last_update_time,
        )
        if limit:
            asset_groups = itertools.islice(asset_groups, limit)
        return asset_groups

    def filter_asset_groups(
            self,
            asset_groups: Iterable[dict],
            asset_group_ids: Optional[Iterable[int]] = None,
            asset_group_names: Optional[Iterable[str]] = None,
            min_asset_group_create_time: Optional[datetime.datetime] = None,
            max_asset_group_create_time: Optional[datetime.datetime] = None,
            min_asset_group_last_update_time: Optional[datetime.datetime] = None,
            max_asset_group_last_update_time: Optional[datetime.datetime] = None):

        for g in asset_groups:

            #: Filter by asset group ID.
            if asset_group_ids and g['id'] not in asset_group_ids:
                continue

            #: Filter by asset group name.
            if asset_group_names and not hodgepodge.pattern_matching.str_matches_glob(g['name'], asset_group_names):
                continue

            #: Filter by creation time.
            if min_asset_group_create_time or max_asset_group_create_time:
                if not hodgepodge.time.in_range(
                    timestamp=g['created_at'],
                    minimum=min_asset_group_create_time,
                    maximum=max_asset_group_create_time,
                ):
                    continue

            #: Filter by last update time.
            if min_asset_group_last_update_time or max_asset_group_last_update_time:
                if not hodgepodge.time.in_range(
                    timestamp=g['updated_at'],
                    minimum=min_asset_group_last_update_time,
                    maximum=max_asset_group_last_update_time,
                ):
                    continue

            yield g

    def count_asset_groups(
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
            max_asset_group_last_update_time: Optional[datetime.datetime] = None) -> int:

        groups = self.iter_asset_groups(
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
        )
        return sum(1 for _ in groups)

    def get_connector(self, connector_id: int) -> Optional[dict]:
        return self._get_object_by_id('connectors', connector_id)

    def iter_connectors(
            self,
            connector_ids: Optional[Iterable[int]] = None,
            connector_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        url = urllib.parse.urljoin(self.url, 'connectors')
        connectors = self._iter_objects(url, limit=limit)
        connectors = self.filter_connectors(
            connectors=connectors,
            connector_ids=connector_ids,
            connector_names=connector_names,
        )
        if limit:
            connectors = itertools.islice(connectors, limit)
        return connectors

    def filter_connectors(
            self,
            connectors: Iterable[dict],
            connector_ids: Optional[Iterable[int]] = None,
            connector_names: Optional[Iterable[str]] = None) -> Iterable[dict]:

        for connector in connectors:

            #: Filter by ID.
            if connector_ids and connector['id'] not in connector_ids:
                continue

            #: Filter by name.
            if connector_names and not hodgepodge.pattern_matching.str_matches_glob(connector['name'], connector_names):
                continue

            yield connector

    def count_connectors(
            self,
            connector_ids: Optional[Iterable[int]] = None,
            connector_names: Optional[Iterable[str]] = None) -> int:

        connectors = self.iter_connectors(
            connector_ids=connector_ids,
            connector_names=connector_names,
        )
        return sum(1 for _ in connectors)

    def count_connector_runs(
            self,
            connector_ids: Optional[Iterable[int]] = None,
            connector_names: Optional[Iterable[str]] = None,
            connector_run_ids: Optional[Iterable[int]] = None) -> int:

        runs = self.get_connector_runs_by_connector_id(
            connector_ids=connector_ids,
            connector_names=connector_names,
            connector_run_ids=connector_run_ids,
        )
        return sum(1 for _ in itertools.chain.from_iterable(runs.values()))

    #: TODO
    def get_connector_run(self, connector_id: int, connector_run_id: int) -> Optional[dict]:
        url = urllib.parse.urljoin(self.url, 'connectors/{}/connector_runs/{}'.format(connector_id, connector_run_id))
        return self._get_object(url)

    def get_connector_runs_by_connector_id(
            self,
            connector_ids: Optional[Iterable[int]] = None,
            connector_names: Optional[Iterable[str]] = None,
            connector_run_ids: Optional[Iterable[int]] = None) -> Dict[int, List[dict]]:

        return dict((connector['id'], runs) for (connector, runs) in self.iter_connector_runs(
            connector_ids=connector_ids,
            connector_names=connector_names,
            connector_run_ids=connector_run_ids,
        ))

    def iter_connector_runs(
            self,
            connector_ids: Optional[Iterable[int]] = None,
            connector_names: Optional[Iterable[str]] = None,
            connector_run_ids: Optional[Iterable[int]] = None) -> Iterator[Tuple[dict, List[dict]]]:

        futures_to_connectors = {}
        connectors_by_id = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for connector in self.iter_connectors(
                connector_ids=connector_ids,
                connector_names=connector_names,
            ):
                connector_id = connector['id']
                connectors_by_id[connector_id] = connector

                url = urllib.parse.urljoin(self.url, 'connectors/{}/connector_runs'.format(connector_id))
                future = executor.submit(self._iter_objects, url=url)
                futures_to_connectors[future] = connector

                connector = futures_to_connectors[future]
                runs = list(future.result())

                #: Filter connector runs by ID.
                if connector_run_ids:
                    runs = list(run for run in runs if run['id'] in connector_run_ids)

                yield connector, runs

    def run_connector(self, connector_id: int):
        url = urllib.parse.urljoin(self.url, 'connectors/{}/run'.format(connector_id))
        response = requests.post(url=url)
        response.raise_for_status()

        return response.json()['connector_run_id']

    def get_dashboard_group(self, dashboard_group_id: int) -> Optional[dict]:
        return self._get_object_by_id('dashboard_groups', dashboard_group_id)

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

        url = urllib.parse.urljoin(self.url, 'dashboard_groups')
        dashboard_groups = self._iter_objects(url=url, limit=limit)
        dashboard_groups = self.filter_dashboard_groups(
            dashboard_groups=dashboard_groups,
            dashboard_group_ids=dashboard_group_ids,
            dashboard_group_names=dashboard_group_names,
            role_ids=role_ids,
            role_names=role_names,
            min_dashboard_group_create_time=min_dashboard_group_create_time,
            max_dashboard_group_create_time=max_dashboard_group_create_time,
            min_dashboard_group_last_update_time=min_dashboard_group_last_update_time,
            max_dashboard_group_last_update_time=max_dashboard_group_last_update_time,
        )
        if limit:
            dashboard_groups = itertools.islice(dashboard_groups, limit)
        return dashboard_groups

    def filter_dashboard_groups(
            self,
            dashboard_groups: Iterable[dict],
            dashboard_group_ids: Optional[Iterable[int]] = None,
            dashboard_group_names: Optional[Iterable[str]] = None,
            role_ids: Optional[Iterable[int]] = None,
            role_names: Optional[Iterable[str]] = None,
            min_dashboard_group_create_time: Optional[datetime.datetime] = None,
            max_dashboard_group_create_time: Optional[datetime.datetime] = None,
            min_dashboard_group_last_update_time: Optional[datetime.datetime] = None,
            max_dashboard_group_last_update_time: Optional[datetime.datetime] = None) -> Iterator[dict]:

        for g in dashboard_groups:

            #: Filter by ID.
            if dashboard_group_ids and g['id'] not in dashboard_group_ids:
                continue

            #: Filter by name.
            if dashboard_group_names and not \
                    hodgepodge.pattern_matching.str_matches_glob(g['name'], dashboard_group_names):
                continue

            #: Filter by creation time.
            if min_dashboard_group_create_time or max_dashboard_group_create_time:
                if not hodgepodge.time.in_range(
                    timestamp=g['created_at'],
                    minimum=min_dashboard_group_create_time,
                    maximum=max_dashboard_group_create_time,
                ):
                    continue

            #: Filter by last update time.
            if min_dashboard_group_last_update_time or max_dashboard_group_last_update_time:
                if not hodgepodge.time.in_range(
                    timestamp=g['updated_at'],
                    minimum=min_dashboard_group_last_update_time,
                    maximum=max_dashboard_group_last_update_time,
                ):
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
                if not hodgepodge.pattern_matching.str_matches_glob(a, b):
                    continue

            yield g

    def count_dashboard_groups(
            self,
            dashboard_group_ids: Optional[Iterable[int]] = None,
            dashboard_group_names: Optional[Iterable[str]] = None,
            role_ids: Optional[Iterable[int]] = None,
            role_names: Optional[Iterable[str]] = None,
            min_dashboard_group_create_time: Optional[datetime.datetime] = None,
            max_dashboard_group_create_time: Optional[datetime.datetime] = None,
            min_dashboard_group_last_update_time: Optional[datetime.datetime] = None,
            max_dashboard_group_last_update_time: Optional[datetime.datetime] = None) -> int:

        groups = self.iter_dashboard_groups(
            dashboard_group_ids=dashboard_group_ids,
            dashboard_group_names=dashboard_group_names,
            role_ids=role_ids,
            role_names=role_names,
            min_dashboard_group_create_time=hodgepodge.time.to_datetime(min_dashboard_group_create_time),
            max_dashboard_group_create_time=hodgepodge.time.to_datetime(max_dashboard_group_create_time),
            min_dashboard_group_last_update_time=hodgepodge.time.to_datetime(min_dashboard_group_last_update_time),
            max_dashboard_group_last_update_time=hodgepodge.time.to_datetime(max_dashboard_group_last_update_time),
        )
        return sum(1 for _ in groups)

    def get_fix(self, fix_id: int) -> Optional[dict]:
        url = urllib.parse.urljoin(self.url, 'fixes/{}'.format(fix_id))
        return self._get_object(url)

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
        url = urllib.parse.urljoin(self.url, 'fixes')
        fixes = self._iter_objects(url, limit=limit)
        fixes = self.filter_fixes(
            fixes=fixes,
            fix_ids=fix_ids,
            fix_names=fix_names,
            fix_vendors=fix_vendors,
            cve_ids=cve_ids,
            asset_ids=asset_ids,
            min_fix_create_time=min_fix_create_time,
            max_fix_create_time=max_fix_create_time,
            min_fix_last_update_time=min_fix_last_update_time,
            max_fix_last_update_time=max_fix_last_update_time,
        )
        if limit:
            fixes = itertools.islice(fixes, limit)
        return fixes

    def filter_fixes(
            self,
            fixes: Iterable[dict],
            fix_ids: Optional[Iterable[int]] = None,
            fix_names: Optional[Iterable[str]] = None,
            fix_vendors: Optional[Iterable[str]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            asset_ids: Optional[Iterable[int]] = None,
            min_fix_create_time: Optional[datetime.datetime] = None,
            max_fix_create_time: Optional[datetime.datetime] = None,
            min_fix_last_update_time: Optional[datetime.datetime] = None,
            max_fix_last_update_time: Optional[datetime.datetime] = None) -> Iterator[dict]:

        for fix in fixes:

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
            if fix_names and not hodgepodge.pattern_matching.str_matches_glob(fix['title'], fix_names):
                continue

            #: Filter by vendor name.
            if fix_vendors and not hodgepodge.pattern_matching.str_matches_glob(fix['vendor'], fix_vendors):
                continue

            #: Filter by CVE ID.
            if cve_ids:
                a = set(fix['cves'])
                b = set(cve_ids)
                if not (a & b):
                    continue

            #: Filter by creation time.
            if min_fix_create_time or max_fix_create_time:
                if not hodgepodge.time.in_range(
                    timestamp=fix['patch_publication_date'],
                    minimum=min_fix_create_time,
                    maximum=max_fix_create_time,
                ):
                    continue

            #: Filter by last update time.
            if min_fix_last_update_time or max_fix_last_update_time:
                if not hodgepodge.time.in_range(
                    timestamp=fix['updated_at'],
                    minimum=min_fix_last_update_time,
                    maximum=max_fix_last_update_time,
                ):
                    continue

            yield fix

    def count_fixes(
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
            max_fix_last_update_time: Optional[datetime.datetime] = None) -> int:

        fixes = self.iter_fixes(
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
        )
        return sum(1 for _ in fixes)

    def get_vulnerability(self, vulnerability_id: int) -> Optional[dict]:
        return self._get_object_by_id('vulnerabilities', vulnerability_id)

    def iter_vulnerabilities(
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
        url = urllib.parse.urljoin(self.url, 'vulnerabilities')
        vulnerabilities = self._iter_objects(url=url, limit=limit)
        vulnerabilities = self.filter_vulnerabilities(
            vulnerabilities=vulnerabilities,
            vulnerability_ids=vulnerability_ids,
            cve_ids=cve_ids,
            fix_ids=fix_ids,
            asset_ids=asset_ids,
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
        )
        if limit:
            vulnerabilities = itertools.islice(vulnerabilities, limit)
        return vulnerabilities

    def filter_vulnerabilities(
            self,
            vulnerabilities: Iterable[dict],
            vulnerability_ids: Optional[Iterable[int]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            fix_ids: Optional[Iterable[int]] = None,
            asset_ids: Optional[Iterable[str]] = None,
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
            max_patch_due_date: Optional[datetime.date] = None) -> Iterator[dict]:

        for vuln in vulnerabilities:

            #: Filter by vulnerability ID.
            if vulnerability_ids and vuln['id'] not in vulnerability_ids:
                continue

            #: Filter by asset ID.
            if asset_ids and vuln['asset_id'] not in asset_ids:
                continue

            #: Filter by fix ID.
            if fix_ids and vuln['fix_id'] not in fix_ids:
                continue

            #: Filter by CVE ID.
            if cve_ids and vuln['cve_id'] not in cve_ids:
                continue

            #: Filter by risk meter score.
            if min_vulnerability_risk_meter_score or max_vulnerability_risk_meter_score:
                if not hodgepodge.math.in_range(
                    value=vuln['risk_meter_score'],
                    minimum=min_vulnerability_risk_meter_score,
                    maximum=max_vulnerability_risk_meter_score,
                ):
                    continue

            #: Filter by create time.
            if min_vulnerability_create_time or max_vulnerability_create_time:
                if not hodgepodge.time.in_range(
                    timestamp=vuln['created_at'],
                    minimum=min_vulnerability_create_time,
                    maximum=max_vulnerability_create_time,
                ):
                    continue

            #: Filter by first seen time.
            if min_vulnerability_first_seen_time or max_vulnerability_first_seen_time:
                if not hodgepodge.time.in_range(
                    timestamp=vuln['first_found_on'],
                    minimum=min_vulnerability_first_seen_time,
                    maximum=max_vulnerability_first_seen_time,
                ):
                    continue

            #: Filter by last seen time.
            if min_vulnerability_last_seen_time or max_vulnerability_last_seen_time:
                if not hodgepodge.time.in_range(
                    timestamp=vuln['last_seen_time'],
                    minimum=min_vulnerability_last_seen_time,
                    maximum=max_vulnerability_last_seen_time,
                ):
                    continue

            #: Filter by CVE publish time.
            if min_cve_publish_time or max_cve_publish_time:
                if not hodgepodge.time.in_range(
                    timestamp=vuln['cve_published_at'],
                    minimum=min_cve_publish_time,
                    maximum=max_cve_publish_time,
                ):
                    continue

            #: Filter by patch publish time.
            if min_patch_publish_time or max_patch_publish_time:
                if not hodgepodge.time.in_range(
                    timestamp=vuln['patch_published_at'],
                    minimum=min_patch_publish_time,
                    maximum=max_patch_publish_time,
                ):
                    continue

            #: Filter by patch due date.
            if min_patch_due_date or max_patch_due_date:
                if not hodgepodge.time.in_range(
                    timestamp=vuln['due_date'],
                    minimum=min_patch_due_date,
                    maximum=max_patch_due_date,
                ):
                    continue

            yield vuln

    def count_vulnerabilities(
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
            max_patch_due_date: Optional[datetime.date] = None) -> int:

        vulnerabilities = self.iter_vulnerabilities(
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
        )
        return sum(1 for _ in vulnerabilities)

    def _get_user_id(self, user_id: Optional[int] = None, user_email_address: Optional[str] = None) -> Optional[int]:
        if user_id:
            return user_id
        elif user_email_address:
            user = next(self.iter_users(user_email_addresses=[user_email_address], limit=1), None)
            if user is None:
                raise NotFoundError("User not found: {}".format(user_email_address))
            else:
                return user['id']
        else:
            raise ValueError("A user ID or e-mail address is required")

    def create_user(
            self,
            email_address: str,
            first_name: str,
            last_name: str,
            role_ids: Optional[Iterable[int]] = None,
            role_names: Optional[Iterable[str]] = None,
            external_id: Optional[str] = None) -> Optional[int]:

        role_ids = list(role_ids) if role_ids else None
        role_names = list(role_names) if role_names else None

        request_parameters = {
            'user': {}
        }
        for k, v in [
            ('firstname', first_name),
            ('lastname', last_name),
            ('email', email_address),
            ('role_ids', role_ids),
            ('roles', role_names),
            ('external_id', external_id),
        ]:
            if v:
                request_parameters['user'][k] = v

        url = urllib.parse.urljoin(self.url, 'users')
        response = self._post(url, data=request_parameters)

        if not response.ok:
            raise WriteError("Failed to create user (request: {}, response: {}, status code: {})".format(
                json.dumps(request_parameters), response.text, response.status_code
            ))
        return response.json()['user']['id']

    def update_user(
            self,
            user_id: int,
            email_address: Optional[str] = None,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            role_ids: Optional[List[int]] = None,
            role_names: Optional[List[str]] = None,
            external_id: Optional[str] = None):

        user = self.get_user(user_id=user_id)
        role_ids = sorted(set(role_ids) | set(user['role_ids'])) if role_ids else None
        role_names = sorted(set(role_names) | set(user['roles'])) if role_names else None

        #: Prepare the request.
        request_parameters = {
            'user': {}
        }
        for k, v in [
            ('firstname', first_name),
            ('lastname', last_name),
            ('email', email_address),
            ('role_ids', role_ids),
            ('roles', role_names),
            ('external_id', external_id),
        ]:
            if v:
                request_parameters['user'][k] = v
        if not request_parameters['user']:
            return

        logger.info("Updating user (%s)",
                    ', '.join('{}={}'.format(k, v) for (k, v) in sorted(request_parameters['user'].items())))

        url = urllib.parse.urljoin(self.url, 'users/{}'.format(user_id))
        response = self._put(url, data=request_parameters)
        if not response.ok:
            raise WriteError("Failed to update user (request: {}, response: {}, status code: {})".format(
                json.dumps(request_parameters), response.text, response.status_code
            ))

    def add_roles_to_user(
            self, user_id: int,
            role_ids: Optional[Iterable[int]] = None,
            role_names: Optional[Iterable[str]] = None):

        if not (role_ids or role_names):
            raise ValueError("A sequence of role IDs or names is required")

        user = self.get_user(user_id=user_id)
        if role_ids:
            role_ids = sorted(set(user['role_ids']) | set(role_ids))
            data = {'user': {'role_ids': role_ids}}
        else:
            role_names = sorted(set(user['roles']) | set(role_names))
            data = {'user': {'roles': role_names}}

        url = urllib.parse.urljoin(self.url, 'users')
        response = self._post(url, data=data)
        response.raise_for_status()

    def get_user(self, user_id: Optional[int] = None, user_email_address: Optional[str] = None):
        if not (user_id or user_email_address):
            raise ValueError("A user ID or e-mail address is required")

        if user_id:
            return self._get_object_by_id('users', user_id)
        else:
            user = next(self.iter_users(user_email_addresses=[user_email_address]), None)
        return user

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
            hide_active_users: Optional[bool] = False,
            hide_inactive_users: Optional[bool] = False,
            limit: Optional[int] = None) -> Iterator[dict]:

        url = urllib.parse.urljoin(self.url, 'users')
        users = self._iter_objects(url, limit=limit)
        users = self.filter_users(
            users=users,
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
            hide_active_users=hide_active_users,
            hide_inactive_users=hide_inactive_users,
        )
        if limit:
            users = itertools.islice(users, limit)
        return users

    def filter_users(
            self,
            users: Iterable[dict],
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
            hide_active_users: Optional[bool] = False,
            hide_inactive_users: Optional[bool] = False) -> Iterator[dict]:

        for user in users:

            #: Filter by ID.
            if user_ids and user['id'] not in user_ids:
                continue

            #: Filter by creation time.
            if min_user_create_time or max_user_create_time:
                if not hodgepodge.time.in_range(
                    timestamp=user['created_at'],
                    minimum=min_user_create_time,
                    maximum=max_user_create_time,
                ):
                    continue

            #: Filter by last update time.
            if min_user_last_update_time or max_user_last_update_time:
                if not hodgepodge.time.in_range(
                    timestamp=user['updated_at'],
                    minimum=min_user_last_update_time,
                    maximum=max_user_last_update_time,
                ):
                    continue

            #: Filter by last sign-in time.
            if hide_active_users and user['last_sign_in_at'] is not None:
                continue

            if hide_inactive_users and user['last_sign_in_at'] is None:
                continue

            if min_user_last_sign_in_time or max_user_last_sign_in_time:
                if not hodgepodge.time.in_range(
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
                values = {value for value in values if value}
                if not hodgepodge.pattern_matching.str_matches_glob(values, user_names):
                    continue

            #: Filter by email address.
            if user_email_addresses:
                if not hodgepodge.pattern_matching.str_matches_glob(user['email'], user_email_addresses):
                    continue

            #: Filter by role ID.
            if role_ids:
                a = set(role_ids)
                b = set(user['role_ids'])
                if not (a & b):
                    continue

            #: Filter by role name.
            if role_names and not hodgepodge.pattern_matching.str_matches_glob(user['roles'], role_names):
                continue

            yield user

    def count_users(
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
            hide_active_users: Optional[bool] = False,
            hide_inactive_users: Optional[bool] = False) -> int:

        users = self.iter_users(
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
            hide_active_users=hide_active_users,
            hide_inactive_users=hide_inactive_users,
        )
        return sum(1 for _ in users)

    def create_role(self, role_name, access_level: str = DEFAULT_ACCESS_LEVEL) -> int:
        request_parameters = {
            'name': role_name,
            'access_level': access_level,
        }
        url = urllib.parse.urljoin(self.url, 'roles')
        response = self._post(url, data=request_parameters)
        if not response.ok:
            raise WriteError("Failed to create role (request: {}, response: {}, status code: {})".format(
                json.dumps(request_parameters), response.text, response.status_code
            ))
        return response.json()['role']['id']

    def update_role(
            self,
            role_id: int,
            name: Optional[str] = None,
            access_level: Optional[str] = None,
            custom_permissions: Optional[Iterable[str]] = None,
            asset_group_ids: Iterable[int] = None,
            application_names: Iterable[str] = None):

        custom_permissions = list(custom_permissions) if custom_permissions else None

        url = urllib.parse.urljoin(self.url, 'roles/{}'.format(role_id))
        request_parameters = {
            'role': {}
        }
        for (k, v) in (
            ('name', name),
            ('access_level', access_level),
            ('asset_group_ids', asset_group_ids),
            ('applications', application_names),
            ('custom_permissions', custom_permissions),
        ):
            if v:
                request_parameters['role'][k] = v
        if not request_parameters['role']:
            return

        #: Update the role.
        response = self._put(url, data=request_parameters)
        response_body = response.json()
        if not response.ok:
            raise WriteError("Failed to update role {} (request: {}, response: {}, status code: {})",
                             role_id, request_parameters, response_body, response.status_code)

    def role_exists(self, role_name):
        roles = self.iter_roles(role_names=[role_name], limit=1)
        role = next(roles, None)
        return role is not None

    def get_role(self, role_id: int) -> Optional[dict]:
        return self._get_object_by_id('roles', role_id)

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
            hide_active_roles: Optional[bool] = False,
            hide_inactive_roles: Optional[bool] = False,
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
        url = urllib.parse.urljoin(self.url, 'roles')
        roles = self._iter_objects(url, limit=limit)
        roles = self.filter_roles(
            roles=roles,
            role_ids=role_ids,
            role_names=role_names,
            role_types=role_types,
            role_access_levels=role_access_levels,
            role_custom_permissions=role_custom_permissions,
            min_role_create_time=min_role_create_time,
            max_role_create_time=max_role_create_time,
            min_role_last_update_time=min_role_last_update_time,
            max_role_last_update_time=max_role_last_update_time,
            hide_active_roles=hide_active_roles,
            hide_inactive_roles=hide_inactive_roles,
        )
        if limit:
            roles = itertools.islice(roles, limit)
        return roles

    def filter_roles(
            self,
            roles: Iterable[dict],
            role_ids: Optional[Iterable[int]] = None,
            role_names: Optional[Iterable[str]] = None,
            role_types: Optional[Iterable[str]] = None,
            role_access_levels: Optional[Iterable[str]] = None,
            role_custom_permissions: Optional[Iterable[str]] = None,
            min_role_create_time: Optional[datetime.datetime] = None,
            max_role_create_time: Optional[datetime.datetime] = None,
            min_role_last_update_time: Optional[datetime.datetime] = None,
            max_role_last_update_time: Optional[datetime.datetime] = None,
            hide_active_roles: Optional[bool] = False,
            hide_inactive_roles: Optional[bool] = False) -> Iterator[dict]:

        #: Lookup users and dashboard groups if filtering roles based on whether they're active/inactive.
        active_roles = set()
        if hide_active_roles or hide_inactive_roles:
            active_roles |= set(itertools.chain.from_iterable(u['role_ids'] for u in self.iter_users()))
            active_roles |= set(itertools.chain.from_iterable(g['role_ids'] for g in self.iter_dashboard_groups()))

        #: Filter roles.
        for role in roles:

            #: Filter by ID.
            if role_ids and role['id'] not in role_ids:
                continue

            #: Optionally hide active roles (i.e. roles that are actively being used).
            if hide_active_roles and (role['asset_groups'] or role['applications'] or role['id'] in active_roles) and \
                    role['role_type'] not in ['system_read', 'system_write']:
                continue

            #: Optionally hide inactive roles (i.e. roles that are no longer being used).
            if hide_inactive_roles and role['id'] not in active_roles:
                continue

            #: Filter by name.
            if role_names and not hodgepodge.pattern_matching.str_matches_glob(role['name'], role_names):
                continue

            #: Filter by type.
            if role_types and not hodgepodge.pattern_matching.str_matches_glob(role['role_type'], role_types):
                continue

            #: Filter by access level.
            if role_access_levels and not \
                    hodgepodge.pattern_matching.str_matches_glob(role['access_level'], role_access_levels):
                continue

            #: Filter by permission name.
            if role_custom_permissions and not \
                    hodgepodge.pattern_matching.str_matches_glob(role['custom_permissions'], role_custom_permissions):
                continue

            #: Filter by creation time.
            if min_role_create_time or max_role_create_time:
                if not hodgepodge.time.in_range(
                    timestamp=role['created_at'],
                    minimum=min_role_create_time,
                    maximum=max_role_create_time,
                ):
                    continue

            #: Filter by last update time.
            if min_role_last_update_time or max_role_last_update_time:
                if not hodgepodge.time.in_range(
                    timestamp=role['updated_at'],
                    minimum=min_role_last_update_time,
                    maximum=max_role_last_update_time,
                ):
                    continue

            yield role

    def count_roles(
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
            hide_active_roles: Optional[bool] = False,
            hide_inactive_roles: Optional[bool] = False) -> int:

        roles = self.iter_roles(
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
            hide_active_roles=hide_active_roles,
            hide_inactive_roles=hide_inactive_roles,
        )
        return sum(1 for _ in roles)

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
            application_ids: Optional[Optional[Iterable[int]]],
            application_names: Optional[Optional[Iterable[str]]] = None) -> List[dict]:

        apps = self.iter_applications(
            application_ids=application_ids,
            application_names=application_names,
        )
        names = {app['team_name'] for app in apps if app['team_name']}
        teams = [{'name': name} for name in names]
        return teams


def _get_object_type_from_url(url: str) -> str:
    path = urllib.parse.urlsplit(url).path
    collection_type = path.lstrip('/').split('/')[0]
    return COLLECTION_TYPES_TO_OBJECT_TYPES[collection_type]


def _get_collection_type_from_url(url: str) -> str:
    path = urllib.parse.urlsplit(url).path
    return path.lstrip('/').split('/')[0]
