from typing import Any, Optional, Iterator, Iterable, List
from kenna import DEFAULT_API_KEY, DEFAULT_REGION
from kenna.constants import APPLICATIONS, MAX_PAGES_ALLOWED_BY_API, ASSETS, CONNECTORS, CONNECTOR_RUNS, \
    DASHBOARD_GROUPS, FIXES, VULNERABILITIES, USERS, ROLES

from hodgepodge.requests import DEFAULT_MAX_RETRIES_ON_REDIRECT, DEFAULT_MAX_RETRIES_ON_CONNECTION_ERRORS, \
    DEFAULT_MAX_RETRIES_ON_READ_ERRORS, DEFAULT_BACKOFF_FACTOR

import requests
import hodgepodge.archives
import hodgepodge.compression
import hodgepodge.files
import hodgepodge.hashing
import hodgepodge.patterns
import hodgepodge.requests
import hodgepodge.requests
import hodgepodge.types
import hodgepodge.time
import hodgepodge.web
import kenna.authentication
import kenna.data.parser
import kenna.region
import logging
import urllib.parse

from kenna.data.types.cve import CVE

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

        policy = hodgepodge.requests.get_automatic_retry_policy(
            max_retries_on_connection_errors=max_retries_on_connection_errors,
            max_retries_on_read_errors=max_retries_on_read_errors,
            max_retries_on_redirects=max_retries_on_redirects,
            backoff_factor=backoff_factor,
        )
        hodgepodge.requests.attach_http_request_policies_to_session(session=self.session, policies=[policy])

    def _get_object(
            self,
            collection_name: str,
            object_id: Optional[int] = None,
            object_name: Optional[str] = None) -> Optional[dict]:

        if collection_name and object_id:
            url = urllib.parse.urljoin(self.url, '{}/{}'.format(collection_name, object_id))
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()

        objects = self._iter_objects(
            collection_name=collection_name,
            object_ids=[object_id] if object_id else None,
            object_names=[object_name] if object_name else None,
        )
        return next(objects, None)

    def _get_objects(
            self,
            collection_name: str,
            url_suffixes: Optional[Iterable[str]] = None,
            object_ids: Optional[Iterable[int]] = None,
            object_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self._iter_objects(
            collection_name=collection_name,
            url_suffixes=url_suffixes,
            object_ids=object_ids,
            object_names=object_names,
            limit=limit,
        ))

    def _iter_objects(
            self,
            collection_name: str,
            url_suffixes: Optional[Iterable[str]] = None,
            object_ids: Optional[Iterable[int]] = None,
            object_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        url_suffixes = url_suffixes or [collection_name]
        if not url_suffixes:
            raise ValueError("An object type or list of URL suffixes is required")

        i = 0
        url = urllib.parse.urljoin(self.url, '/'.join(map(str, url_suffixes)))
        for row in self.__iter_objects(collection_name=collection_name, url=url):

            #: Filter objects by ID.
            if object_ids and row['id'] not in object_ids:
                continue

            #: Filter objects by name.
            if object_names:
                if 'name' not in row:
                    continue

                if not hodgepodge.patterns.string_matches_any_glob(row['name'], object_names, case_sensitive=False):
                    continue

            yield row

            #: Optionally limit the number of search results.
            if limit:
                i += 1
                if i >= limit:
                    break

    def __iter_objects(self, collection_name: str, url: str) -> Iterator[dict]:
        response = self.session.get(url)
        response.raise_for_status()
        page = response.json()

        #: If pagination is not enabled.
        if isinstance(page, list):
            for row in page:
                yield row

        #: If pagination is enabled.
        elif isinstance(page, dict):
            for row in page[collection_name]:
                yield row

            if 'meta' in page:
                meta = page.pop('meta')
                current_page = meta['page']
                total_pages = meta['pages']

                #: Read up to 20 pages of up to 5,000 rows.
                for page_number in range(current_page + 1, min(total_pages, MAX_PAGES_ALLOWED_BY_API)):
                    params = {
                        'page': page_number,
                    }
                    response = self.session.get(url, params=params)
                    response.raise_for_status()

                    page = response.json()
                    for row in page[collection_name]:
                        yield row
        else:
            raise NotImplementedError("Unsupported pagination strategy")

    def get_application(
            self,
            application_id: Optional[int] = None,
            application_name: Optional[str] = None) -> Optional[Any]:

        return self._get_object(
            collection_name=APPLICATIONS,
            object_id=application_id,
            object_name=application_name,
        )

    def get_applications(
            self,
            application_ids: Optional[Iterable[int]] = None,
            application_names: Optional[Optional[Iterable[str]]] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_applications(
            application_ids=application_ids,
            application_names=application_names,
            limit=limit,
        ))

    def iter_applications(
            self,
            application_ids: Optional[Iterable[int]] = None,
            application_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        for app in self._iter_objects(
            collection_name=APPLICATIONS,
            object_ids=application_ids,
            object_names=application_names,
            limit=limit,
        ):
            yield app

    def get_asset(
            self,
            asset_id: Optional[int] = None,
            asset_name: Optional[str] = None) -> Optional[Any]:

        return self._get_object(
            collection_name=ASSETS,
            object_id=asset_id,
            object_name=asset_name,
        )

    def get_assets(
            self,
            asset_ids: Optional[Iterable[int]] = None,
            asset_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_assets(
            asset_ids=asset_ids,
            asset_names=asset_names,
            limit=limit,
        ))

    def iter_assets(self,
                    asset_ids: Optional[Iterable[int]] = None,
                    asset_names: Optional[Iterable[str]] = None,
                    limit: Optional[int] = None) -> Iterator[dict]:

        for asset in self._iter_objects(
            collection_name=ASSETS,
            object_ids=asset_ids,
            object_names=asset_names,
            limit=limit,
        ):
            yield asset

    def get_connector(
            self,
            connector_id: Optional[int] = None,
            connector_name: Optional[str] = None) -> Optional[Any]:

        return self._get_object(
            collection_name=CONNECTORS,
            object_id=connector_id,
            object_name=connector_name,
        )

    def get_connectors(
            self,
            connector_ids: Optional[Iterable[int]] = None,
            connector_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_connectors(
            connector_ids=connector_ids,
            connector_names=connector_names,
            limit=limit,
        ))

    def iter_connectors(
            self,
            connector_ids: Optional[Iterable[int]] = None,
            connector_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        for connector in self._iter_objects(
            collection_name=CONNECTORS,
            object_ids=connector_ids,
            object_names=connector_names,
            limit=limit,
        ):
            yield connector

    def get_connector_runs(
            self,
            connector_ids: Optional[Iterable[int]] = None,
            connector_names: Optional[Iterable[str]] = None,
            connector_run_ids: Optional[Iterable[int]] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_connector_runs(
            connector_ids=connector_ids,
            connector_names=connector_names,
            connector_run_ids=connector_run_ids,
            limit=limit,
        ))

    def iter_connector_runs(
            self,
            connector_ids: Optional[Iterable[int]] = None,
            connector_names: Optional[Iterable[str]] = None,
            connector_run_ids: Optional[Iterable[int]] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        i = 0
        for connector in self.iter_connectors(connector_ids=connector_ids, connector_names=connector_names):
            for run in self._iter_objects(
                collection_name=CONNECTOR_RUNS,
                url_suffixes=[CONNECTORS, connector['id'], CONNECTOR_RUNS],
                object_ids=connector_run_ids,
            ):
                yield run

                i += 1
                if limit and i >= limit:
                    return

    def get_connector_run(
            self,
            connector_id: Optional[int] = None,
            connector_name: Optional[str] = None,
            connector_run_id: Optional[int] = None):

        runs = self.iter_connector_runs(
            connector_ids=[connector_id] if connector_id else None,
            connector_names=[connector_name] if connector_name else None,
            connector_run_ids=[connector_run_id] if connector_run_id else None,
        )
        return next(runs, None)

    def get_dashboard_group(
            self,
            dashboard_group_id: Optional[int] = None,
            dashboard_group_name: Optional[str] = None) -> Optional[Any]:

        return self._get_object(
            collection_name=DASHBOARD_GROUPS,
            object_id=dashboard_group_id,
            object_name=dashboard_group_name,
        )

    def get_dashboard_groups(
            self,
            dashboard_group_ids: Optional[Iterable[int]] = None,
            dashboard_group_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_dashboard_groups(
            dashboard_group_ids=dashboard_group_ids,
            dashboard_group_names=dashboard_group_names,
            limit=limit,
        ))

    def iter_dashboard_groups(
            self,
            dashboard_group_ids: Optional[Iterable[int]] = None,
            dashboard_group_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        for dashboard_group in self._iter_objects(
            collection_name=DASHBOARD_GROUPS,
            object_ids=dashboard_group_ids,
            object_names=dashboard_group_names,
            limit=limit,
        ):
            yield dashboard_group

    def get_fix(
            self,
            fix_id: Optional[int] = None,
            fix_name: Optional[str] = None) -> Optional[Any]:

        return self._get_object(
            collection_name=FIXES,
            object_id=fix_id,
            object_name=fix_name,
        )

    def get_fixes(
            self,
            fix_ids: Optional[Iterable[int]] = None,
            fix_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_fixes(
            fix_ids=fix_ids,
            fix_names=fix_names,
            limit=limit,
        ))

    def iter_fixes(
            self,
            fix_ids: Optional[Iterable[int]] = None,
            fix_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        for fix in self._iter_objects(
            collection_name=FIXES,
            object_ids=fix_ids,
            object_names=fix_names,
            limit=limit,
        ):
            yield fix

    def get_vulnerability(
            self,
            vulnerability_id: Optional[int] = None,
            vulnerability_name: Optional[str] = None) -> Optional[Any]:

        return self._get_object(
            collection_name=VULNERABILITIES,
            object_id=vulnerability_id,
            object_name=vulnerability_name,
        )

    def get_vulnerabilities(
            self,
            vulnerability_ids: Optional[Iterable[int]] = None,
            vulnerability_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_vulnerabilities(
            vulnerability_ids=vulnerability_ids,
            vulnerability_names=vulnerability_names,
            limit=limit,
        ))

    def iter_vulnerabilities(
            self,
            vulnerability_ids: Optional[Iterable[int]] = None,
            vulnerability_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        for vulnerability in self._iter_objects(
            collection_name=VULNERABILITIES,
            object_ids=vulnerability_ids,
            object_names=vulnerability_names,
            limit=limit,
        ):
            yield vulnerability

    def get_cves(
            self,
            vulnerability_ids: Optional[Iterable[int]] = None,
            vulnerability_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        return list(self.iter_cves(
            vulnerability_ids=vulnerability_ids,
            vulnerability_names=vulnerability_names,
            limit=limit,
        ))

    def iter_cves(
            self,
            vulnerability_ids: Optional[Iterable[int]] = None,
            vulnerability_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        i = 0
        cves = set()
        vulns = self.iter_vulnerabilities(
            vulnerability_ids=vulnerability_ids,
            vulnerability_names=vulnerability_names,
        )
        for vuln in vulns:
            cve = CVE(
                id=vuln['cve_id'],
                description=vuln['cve_description'],
                create_time=hodgepodge.time.convert_time_to_datetime(vuln['cve_published_at']),
            )
            if cve not in cves:
                yield hodgepodge.types.dataclass_to_dict(cve)
                
                if limit:
                    i += 1
                    if i >= limit:
                        break

    def get_user(
            self,
            user_id: Optional[int] = None,
            user_name: Optional[str] = None) -> Optional[Any]:

        return self._get_object(
            collection_name=USERS,
            object_id=user_id,
            object_name=user_name,
        )

    def get_users(
            self,
            user_ids: Optional[Iterable[int]] = None,
            user_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_users(
            user_ids=user_ids,
            user_names=user_names,
            limit=limit,
        ))

    def iter_users(
            self,
            user_ids: Optional[Iterable[int]] = None,
            user_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        for user in self._iter_objects(
            collection_name=USERS,
            object_ids=user_ids,
            object_names=user_names,
            limit=limit,
        ):
            yield user

    def get_role(
            self,
            role_id: Optional[int] = None,
            role_name: Optional[str] = None) -> Optional[Any]:

        return self._get_object(
            collection_name=ROLES,
            object_id=role_id,
            object_name=role_name,
        )

    def get_roles(
            self,
            role_ids: Optional[Iterable[int]] = None,
            role_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> List[dict]:

        return list(self.iter_roles(
            role_ids=role_ids,
            role_names=role_names,
            limit=limit,
        ))

    def iter_roles(
            self,
            role_ids: Optional[Iterable[int]] = None,
            role_names: Optional[Iterable[str]] = None,
            limit: Optional[int] = None) -> Iterator[dict]:

        for role in self._iter_objects(
            collection_name=ROLES,
            object_ids=role_ids,
            object_names=role_names,
            limit=limit,
        ):
            yield role

    def get_business_units(
            self,
            application_ids: Optional[Optional[Iterable[str]]],
            application_names: Optional[Optional[Iterable[str]]] = None) -> List[dict]:

        apps = self.iter_applications(application_ids=application_ids, application_names=application_names)
        names = {app['business_units'] for app in apps if app['business_units']}
        units = [{'name': name} for name in names]
        return units

    def get_teams(self,
                  application_ids: Optional[Optional[Iterable[str]]],
                  application_names: Optional[Optional[Iterable[str]]] = None) -> List[dict]:

        apps = self.iter_applications(
            application_ids=application_ids,
            application_names=application_names,
        )
        names = {app['team_name'] for app in apps if app['team_name']}
        teams = [{'name': name} for name in names]
        return teams
