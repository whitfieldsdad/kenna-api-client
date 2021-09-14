from typing import Any, Optional, List, Iterator, Dict
from kenna import DEFAULT_API_KEY, DEFAULT_REGION
from hodgepodge.requests import DEFAULT_MAX_RETRIES_ON_REDIRECT, DEFAULT_MAX_RETRIES_ON_CONNECTION_ERRORS, \
    DEFAULT_MAX_RETRIES_ON_READ_ERRORS, DEFAULT_BACKOFF_FACTOR

import logging
import urllib.parse
import requests
import hodgepodge.archives
import hodgepodge.compression
import hodgepodge.files
import hodgepodge.hashing
import hodgepodge.requests
import hodgepodge.requests
import hodgepodge.time
import hodgepodge.web
import hodgepodge.patterns
import kenna.authentication
import kenna.data.parser
import kenna.region
import itertools
import datetime

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

_MAX_PAGES_ALLOWED_BY_API = 20


class _Kenna:
    def __init__(self, api_key: str = DEFAULT_API_KEY, region: str = DEFAULT_REGION,
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

    def _get_object(self, object_type: str, object_id: int) -> Dict[str, Any]:
        url = urllib.parse.urljoin(self.url, '{}/{}'.format(object_type, object_id))
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    #: TODO
    def _iter_objects(self, object_type: str, object_ids: List[str] = None, object_names: List[str] = None,
                      min_create_time: Optional[datetime.datetime] = None, max_create_time: Optional[datetime.datetime] = None,
                      min_update_time: Optional[datetime.datetime] = None, max_update_time: Optional[datetime.datetime] = None,
                      url_suffixes: List[str] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:

        url_suffixes = url_suffixes or [object_type]
        if not url_suffixes:
            raise ValueError("An object type or list of URL suffixes is required")

        i = 0
        url = urllib.parse.urljoin(self.url, '/'.join(url_suffixes))
        for row in self.__iter_objects(object_type=object_type, url=url):

            #: Filter objects by ID.
            if object_ids and row['id'] not in object_ids:
                continue

            #: Filter objects by name.
            if object_names and row['name'] not in object_names:
                continue

            #: Filter objects by create time.
            if min_create_time or max_create_time:
                create_time = hodgepodge.time.as_datetime(row['created_at'])
                if not hodgepodge.time.is_within_range(create_time, min_create_time, max_create_time):
                    continue

            #: Filter objects by last update time.
            if min_update_time or max_update_time:
                update_time = hodgepodge.time.as_datetime(row['created_at'])
                if not hodgepodge.time.is_within_range(update_time, min_update_time, max_update_time):
                    continue

            yield row

            if limit:
                i += 1
                if i >= limit:
                    break

    def __iter_objects(self, object_type, url: str) -> Any:
        response = self.session.get(url)
        response.raise_for_status()
        page = response.json()

        if isinstance(page, list):
            for row in page:
                yield row

        elif isinstance(page, dict):
            for row in page[object_type]:
                yield row

            meta = page.pop('meta')
            current_page = meta['page']
            total_pages = meta['pages']

            for page_number in range(current_page + 1, min(total_pages, _MAX_PAGES_ALLOWED_BY_API)):
                params = {
                    'page': page_number,
                }
                response = self.session.get(url, params=params)
                response.raise_for_status()

                page = response.json()
                for row in page[object_type]:
                    yield row
        else:
            raise NotImplementedError("Unsupported pagination strategy")

    def get_application(self, application_id: int) -> Optional[Any]:
        logger.info("Looking up application (application ID: %s)", application_id)
        return self._get_object('applications', object_id=application_id)

    def get_applications(self, application_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_applications(application_ids=application_ids, limit=limit))

    def iter_applications(self, application_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up applications (application IDs: %s)", application_ids)
        for app in self._iter_objects('applications', limit=limit):
            yield app

    def get_asset(self, asset_id: int) -> Optional[Any]:
        logger.info("Looking up asset (asset ID: %s)", asset_id)
        return self._get_object('assets', object_id=asset_id)

    def get_assets(self, asset_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_assets(asset_ids=asset_ids, limit=limit))

    def iter_assets(self, asset_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up assets (asset IDs: %s)", asset_ids)
        for asset in self._iter_objects('assets', limit=limit):
            yield asset

    def get_connector(self, connector_id: int) -> Optional[Any]:
        logger.info("Looking up connector (connector ID: %s)", connector_id)
        return self._get_object(object_type='connectors', object_id=connector_id)

    def get_connectors(self, connector_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_connectors(connector_ids=connector_ids, limit=limit))

    def iter_connectors(self, connector_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up connectors (connector IDs: %s)", connector_ids)
        for connector in self._iter_objects(
                object_type='connectors',
                object_ids=connector_ids,
                limit=limit,
        ):
            yield connector

    def get_connector_runs(self, connector_run_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_connector_runs(connector_run_ids=connector_run_ids, limit=limit))

    #: TODO
    def iter_connector_runs(self, connector_ids: List[int] = None,
                            connector_run_ids: List[int] = None,
                            limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:

        logger.info("Looking up connector runs (connector IDs: %s, connector run IDs: %s)", connector_ids,
                    connector_run_ids)
        i = 0
        for connector in self.iter_connectors(connector_ids=connector_ids):
            url = urllib.parse.urljoin(self.url, '{}/{}/{}'.format('connectors', connector['id'], 'connector_runs'))
            for run in self._iter_objects_by_url(url):
                if connector_run_ids and run['id'] not in connector_run_ids:
                    continue

                yield run

                i += 1
                if limit and i >= limit:
                    break

    def get_connector_run(self, connector_id: int, connector_run_id: int):
        return next(self.iter_connector_runs(connector_ids=[connector_id], connector_run_ids=[connector_run_id]), None)

    def get_dashboard_group(self, dashboard_group_id: int) -> Optional[Any]:
        logger.info("Looking up dashboard group (dashboard group ID: %s)", dashboard_group_id)
        return self._get_object(object_type='dashboard_groups', object_id=dashboard_group_id)

    def get_dashboard_groups(self, dashboard_group_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_dashboard_groups(dashboard_group_ids=dashboard_group_ids, limit=limit))

    def iter_dashboard_groups(self, dashboard_group_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up dashboard groups (dashboard group IDs: %s)", dashboard_group_ids)
        for dashboard_group in self._iter_objects(
            object_type='dashboard_groups',
            object_ids=dashboard_group_ids,
            limit=limit,
        ):
            yield dashboard_group

    def get_fix(self, fix_id: int) -> Optional[Any]:
        logger.info("Looking up fix (fix ID: %s)", fix_id)
        return self._get_object(object_type='fixes', object_id=fix_id)

    def get_fixes(self, fix_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_fixes(fix_ids=fix_ids, limit=limit))

    def iter_fixes(self, fix_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up fixes (fix IDs: %s)", fix_ids)
        for fix in self._iter_objects(
            object_type='fixes',
            object_ids=fix_ids,
            limit=limit,
        ):
            yield fix

    def get_vulnerability(self, vulnerability_id: int) -> Optional[Any]:
        logger.info("Looking up vulnerability (vulnerability ID: %s)", vulnerability_id)
        return self._get_object(object_type='vulnerabilities', object_id=vulnerability_id)

    def get_vulnerabilities(self, vulnerability_ids: List[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.iter_vulnerabilities(vulnerability_ids=vulnerability_ids, limit=limit))

    def iter_vulnerabilities(self, vulnerability_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        logger.info("Looking up vulnerability IDs (vulnerability IDs: %s)", vulnerability_ids)
        for vulnerability in self._iter_objects(
            object_type='vulnerabilities',
            object_ids=vulnerability_ids,
            limit=limit,
        ):
            yield vulnerability

    def get_user(self, user_id: int) -> Optional[Any]:
        logger.info("Looking up user (user ID: %s)", user_id)
        return self._get_object(object_type='users', object_id=user_id)

    def get_users(self, user_ids: List[int] = None, user_names: List[str] = None, role_ids: List[int] = None,
                  role_names: List[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:

        return list(self.iter_users(
            user_ids=user_ids,
            user_names=user_names,
            role_ids=role_ids,
            role_names=role_names,
            limit=limit,
        ))

    def iter_users(self, user_ids: List[int] = None, user_names: List[str] = None, role_ids: List[int] = None,
                   role_names: List[str] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:

        logger.info("Looking up users (user IDs: %s, user names: %s, role IDs: %s, role names: %s",
                    user_ids, user_names, role_ids, role_names)

        users = self._iter_objects(object_type='users', object_ids=user_ids, limit=limit)
        for user in users:

            #: Filter users by name.
            if user_names:
                name = ' '.join([name for name in (user['firstname'], user['lastname']) if name])
                if not hodgepodge.patterns.string_matches_any_glob(name, user_names):
                    continue

            #: Filter users by role ID.
            if role_ids and set(user['role_ids']).isdisjoint(set(role_ids)):
                continue

            #: Filter users by role name.
            if role_names and not hodgepodge.patterns.any_string_matches_any_glob(user['roles'], role_names):
                continue

            yield user

    def get_role(self, role_id: int) -> Optional[Any]:
        logger.info("Looking up role (role ID: %s)", role_id)
        return self._get_object(object_type='roles', object_id=role_id)

    def get_roles(self, role_ids: List[int] = None, role_names: List[str] = None, user_ids: List[str] = None,
                  user_names: List[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:

        return list(self.iter_roles(
            role_ids=role_ids,
            role_names=role_names,
            user_ids=user_ids,
            user_names=user_names,
            limit=limit,
        ))

    def iter_roles(self, role_ids: List[int] = None, role_names: List[str] = None, user_ids: List[str] = None,
                   user_names: List[str] = None, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:

        logger.info("Looking up roles (role IDs: %s, role names: %s, user IDs: %s, user names: %s)",
                    role_ids, role_names, user_ids, user_names)

        #: Filter roles by user.
        if user_ids or user_names:
            users = self.get_users(
                user_ids=user_ids,
                user_names=user_names,
                role_ids=role_ids,
                role_names=role_names,
            )
            role_ids = set(itertools.chain.from_iterable(user['role_ids'] for user in users))
            role_names = None

        #: Lookup roles.
        roles = self._iter_objects(
            object_type='roles',
            object_ids=role_ids,
            limit=limit,
        )
        for role in roles:

            #: Filter roles by name.
            if role_names and not hodgepodge.patterns.string_matches_any_glob(role['name'], role_names):
                continue

            yield role


class Kenna:
    def __init__(self, api_key: str = DEFAULT_API_KEY, region: str = DEFAULT_REGION,
                 max_retries_on_connection_errors: int = DEFAULT_MAX_RETRIES_ON_CONNECTION_ERRORS,
                 max_retries_on_read_errors: int = DEFAULT_MAX_RETRIES_ON_READ_ERRORS,
                 max_retries_on_redirects: int = DEFAULT_MAX_RETRIES_ON_REDIRECT,
                 backoff_factor: float = DEFAULT_BACKOFF_FACTOR):

        self.raw = _Kenna(
            api_key=api_key,
            region=region,
            max_retries_on_connection_errors=max_retries_on_connection_errors,
            max_retries_on_read_errors=max_retries_on_read_errors,
            max_retries_on_redirects=max_retries_on_redirects,
            backoff_factor=backoff_factor,
        )

    def get_application(self, application_id: int) -> Optional[Any]:
        return self.raw.get_application(application_id=application_id)

    def get_applications(self, application_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_applications(application_ids=application_ids, limit=limit))

    def iter_applications(self, application_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for app in self.raw.iter_applications(application_ids=application_ids, limit=limit):
            yield app

    def get_asset(self, asset_id: int) -> Optional[Any]:
        return self.raw.get_asset(asset_id=asset_id)

    def get_assets(self, asset_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_assets(asset_ids=asset_ids, limit=limit))

    def iter_assets(self, asset_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for asset in self.raw.iter_assets(asset_ids=asset_ids, limit=limit):
            yield asset

    def get_connector(self, connector_id: int) -> Optional[Any]:
        return self.raw.get_connector(connector_id=connector_id)

    def get_connectors(self, connector_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_connectors(connector_ids=connector_ids, limit=limit))

    def iter_connectors(self, connector_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for connector in self.raw.iter_connectors(connector_ids=connector_ids, limit=limit):
            yield connector

    def get_connector_runs(self, connector_ids: List[int] = None, connector_run_ids: List[int] = None,
                           limit: Optional[int] = None) -> List[Any]:

        return list(self.iter_connector_runs(
            connector_ids=connector_ids,
            connector_run_ids=connector_run_ids,
            limit=limit,
        ))

    def iter_connector_runs(self, connector_ids: List[int] = None, connector_run_ids: List[int] = None,
                            limit: Optional[int] = None) -> Iterator[Any]:

        for run in self.raw.iter_connector_runs(
            connector_ids=connector_ids,
            connector_run_ids=connector_run_ids,
            limit=limit,
        ):
            yield run

    def get_connector_run(self, connector_id: int, connector_run_id: int) -> Optional[Any]:
        return self.raw.get_connector_run(connector_id=connector_id, connector_run_id=connector_run_id)
    
    def get_dashboard_group(self, dashboard_group_id: int) -> Optional[Any]:
        return self.raw.get_dashboard_group(dashboard_group_id=dashboard_group_id)

    def get_dashboard_groups(self, dashboard_group_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_dashboard_groups(dashboard_group_ids=dashboard_group_ids, limit=limit))

    def iter_dashboard_groups(self, dashboard_group_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for dashboard_group in self.raw.iter_dashboard_groups(dashboard_group_ids=dashboard_group_ids, limit=limit):
            yield dashboard_group
    
    def get_fix(self, fix_id: int) -> Optional[Any]:
        return self.raw.get_fix(fix_id=fix_id)

    def get_fixes(self, fix_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_fixes(fix_ids=fix_ids, limit=limit))

    def iter_fixes(self, fix_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for fix in self.raw.iter_fixes(fix_ids=fix_ids, limit=limit):
            yield fix
    
    def get_vulnerability(self, vulnerability_id: int) -> Optional[Any]:
        return self.raw.get_vulnerability(vulnerability_id=vulnerability_id)

    def get_vulnerabilities(self, vulnerability_ids: List[int] = None, limit: Optional[int] = None) -> List[Any]:
        return list(self.iter_vulnerabilities(vulnerability_ids=vulnerability_ids, limit=limit))

    def iter_vulnerabilities(self, vulnerability_ids: List[int] = None, limit: Optional[int] = None) -> Iterator[Any]:
        for vulnerability in self.raw.iter_vulnerabilities(vulnerability_ids=vulnerability_ids, limit=limit):
            yield vulnerability

    def get_user(self, user_id: int) -> Optional[Any]:
        return self.raw.get_user(user_id=user_id)

    def get_users(self, user_ids: List[int] = None, user_names: List[str] = None, role_ids: List[int] = None,
                  role_names: List[str] = None, limit: Optional[int] = None) -> List[Any]:

        return list(self.iter_users(
            user_ids=user_ids,
            user_names=user_names,
            role_ids=role_ids,
            role_names=role_names,
            limit=limit,
        ))

    def iter_users(self, user_ids: List[int] = None, user_names: List[str] = None, role_ids: List[int] = None,
                   role_names: List[str] = None, limit: Optional[int] = None) -> Iterator[Any]:

        return self.raw.iter_users(
            user_ids=user_ids,
            user_names=user_names,
            role_ids=role_ids,
            role_names=role_names,
            limit=limit,
        )

    def get_role(self, role_id: Optional[int] = None, role_name: Optional[str] = None) -> Optional[Any]:
        if role_id:
            return self.raw.get_role(role_id=role_id)
        elif role_name:
            return next(self.iter_roles(role_names=[role_name]), None)
        else:
            return next(self.iter_roles(), None)

    def get_roles(self, role_ids: List[int] = None, role_names: List[str] = None, user_ids: List[int] = None,
                  user_names: List[str] = None, limit: Optional[int] = None) -> List[Any]:

        return list(self.iter_roles(
            role_ids=role_ids,
            role_names=role_names,
            user_ids=user_ids,
            user_names=user_names,
            limit=limit,
        ))

    def iter_roles(self, role_ids: List[int] = None, role_names: List[str] = None, user_ids: List[int] = None,
                   user_names: List[str] = None, limit: Optional[int] = None) -> Iterator[Any]:

        for role in self.raw.iter_roles(
            role_ids=role_ids,
            role_names=role_names,
            user_ids=user_ids,
            user_names=user_names,
            limit=limit,
        ):
            yield role
