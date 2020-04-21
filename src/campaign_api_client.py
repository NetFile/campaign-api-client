#!/usr/bin/python

from src import *
from enum import Enum
import argparse
import requests

import sys
sys.path.append('../')

logger = logging.getLogger(__name__)


class Routes:
    SYSTEM_REPORT = '/system'
    SYNC_FEED = '/%s/v101/sync/feeds'
    SYNC_SUBSCRIPTIONS = '/%s/v101/sync/subscriptions'
    SYNC_SESSIONS = '/%s/v101/sync/sessions'

    # First parameter is Session ID. Second parameter is Command Type
    SYNC_SESSION_COMMAND = '/%s/v101/sync/sessions/%s/commands/%s'

    # First parameter is Subscription ID. Second parameter is Command Type
    SYNC_SUBSCRIPTION_COMMAND = '/%s/v101/sync/subscriptions/%s/commands/%s'

    # Parameter is the Subscription ID
    FETCH_SUBSCRIPTION = '/%s/v101/sync/subscriptions/%s'

    # First parameter is the Root Filing NID
    FETCH_FILING = '/cal/v101/filings/%s'
    FETCH_EFILE_CONTENT = '/cal/v101/filings/%s/contents/efiling'
    QUERY_FILINGS = '/cal/v101/filings'

    # First parameter is the Element ID
    FETCH_FILING_ELEMENTS = '/cal/v101/filing-elements/%s'
    QUERY_FILING_ELEMENTS = '/cal/v101/filing-elements'


class CampaignApiClient:
    """Provides support for synchronizing local database with Campaign API filing data"""

    def __init__(self, base_url, api_key, api_password, agency_id):
        self.headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        self.base_url = base_url
        self.user = api_key
        self.password = api_password
        self.agency_id = agency_id

    def fetch_system_report(self):
        logger.debug('Checking to verify the Campaign API system is ready')
        url = self.base_url + Routes.SYSTEM_REPORT
        sr = self.get_http_request(url)
        logger.debug('General Status: %s', sr['generalStatus'])
        logger.debug('System Name: %s', sr['name'])
        for comp in sr['components']:
            logger.debug('\tComponent Name: %s', comp['name'])
            logger.debug('\tComponent Message: %s', comp['message'])
            logger.debug('\tComponent status: %s', comp['status'])
            logger.debug('\tComponent Build DateTime: %s',
                         comp['buildDateTime'])
            logger.debug('\tComponent Build Version: %s', comp['buildVersion'])
        return sr

    def peek_subscription(self, domain, sub_id):
        logger.debug(f"Peeking SyncSubscription with id: {sub_id}")
        ext = Routes.FETCH_SUBSCRIPTION % (domain, sub_id)
        url = self.base_url + ext + '/peek'
        return self.get_http_request(url)

    def create_subscription(self, domain, feed_name_arg, subscription_name_arg):
        logger.debug('Creating a SyncSubscription')
        url = self.base_url + Routes.SYNC_SUBSCRIPTIONS % (domain)
        body = {
            'feedName': feed_name_arg,
            'name': subscription_name_arg
        }
        return self.post_http_request(url, body)

    def fetch_subscription(self, domain, sub_id):
        logger.debug(f"Fetching SyncSubscription with id: {sub_id}")
        ext = Routes.FETCH_SUBSCRIPTION % (domain, sub_id)
        url = self.base_url + ext
        return self.get_http_request(url)

    def execute_subscription_command(self, domain, sub_id, subscription_command_type):
        logger.debug(
            f"Executing {subscription_command_type} SyncSubscription command")
        ext = Routes.SYNC_SUBSCRIPTION_COMMAND % (
            domain, sub_id, subscription_command_type)
        url = self.base_url + ext
        body = {
            'id': sub_id
        }
        return self.post_http_request(url, body)

    def query_subscriptions(self, domain, feed_id, limit=1000, offset=0):
        logger.debug('Retrieving available subscriptions\n')
        params = {'feedId': feed_id, 'status': 'Active',
                  'limit': limit, 'offset': offset}
        url = self.base_url + Routes.SYNC_SUBSCRIPTIONS % domain
        return self.get_http_request(url, params)

    def create_session(self, domain, sub_id):
        logger.debug(f'Creating a SyncSession using SyncSubscription {sub_id}')
        url = f'{self.base_url}/{Routes.SYNC_SESSIONS % domain}'
        body = {
            'subscriptionId': sub_id
        }
        return self.post_http_request(url, body)

    def execute_session_command(self, domain, session_id, session_command_type):
        logger.debug(f'Executing {session_command_type} SyncSession command')
        url = self.base_url + \
            Routes.SYNC_SESSION_COMMAND % (
                domain, session_id, session_command_type)
        return self.post_http_request(url)

    def fetch_sync_topic(self, domain, session_id, topic, limit=1000, offset=0):
        logger.debug(
            f'Fetching {topic} topic: offset={offset}, limit={limit}\n')
        params = {'limit': limit, 'offset': offset}
        url = f'{self.base_url}/{Routes.SYNC_SESSIONS % domain}/{session_id}/{topic}'
        return self.get_http_request(url, params)

    def retrieve_sync_feeds(self, domain):
        logger.debug('Retrieving SyncFeed')
        url = self.base_url + Routes.SYNC_FEED % domain
        return self.get_http_request(url)

    def fetch_filings(self, root_filing_nid):
        logger.debug(f'Fetching filing {root_filing_nid}')
        url = self.base_url + Routes.FETCH_FILING % root_filing_nid
        return self.get_http_request(url)

    def query_filings(self, query):
        logger.debug('Querying filings')
        url = self.base_url + Routes.QUERY_FILINGS
        params = {'Origin': query.origin, 'FilingId': query.filing_id, 'FilingSpecification': query.filing_specification,
                  'limit': query.limit, 'offset': query.offset}
        headers = {
            'Accept': 'application/json'
        }
        return self.get_http_request(url, params, headers)

    def fetch_filing_element(self, element_nid):
        logger.debug(f'Fetching filing {element_nid}')
        url = self.base_url + Routes.FETCH_FILING_ELEMENTS % element_nid
        return self.get_http_request(url)

    def query_filing_elements(self, query):
        logger.debug('Querying Filing Elements')
        url = self.base_url + Routes.QUERY_FILING_ELEMENTS
        params = {'Origin': query.origin, 'FilingId': query.filing_id,
                  'ElementClassification': query.element_classification, 'ElementType': query.element_type,
                  'limit': query.limit, 'offset': query.offset}
        headers = {
            'Accept': 'application/json'
        }
        return self.get_http_request(url, params, headers)

    def fetch_efile_content(self, root_filing_nid):
        logger.debug('Fetching Efile Content')
        url = self.base_url + Routes.FETCH_EFILE_CONTENT % root_filing_nid
        logger.debug(f'Making GET HTTP request to {url}')
        response = requests.get(url, params={'contentType': 'efile'}, auth=(
            self.user, self.password), headers=self.headers)
        if response.status_code not in [200, 201]:
            raise Exception(
                f'Error requesting Url: {url}, Response code: {response.status_code}. Error Message: {response.text}')
        file_content = response.text
        return file_content

    def post_http_request(self, url, body=None):
        logger.debug(f'Making POST HTTP request to {url}')
        try:
            params = {'aid': self.agency_id}
            response = requests.post(url, auth=(self.user, self.password), data=json.dumps(
                body), headers=self.headers, params=params)
        except Exception as ex:
            logger.error(ex)
            sys.exit()
        if response.status_code not in [200, 201]:
            raise Exception(
                f'Error requesting Url: {url}, Response code: {response.status_code}. Error Message: {response.text}')
        return response.json()

    def get_http_request(self, url, params={}, headers=None):
        logger.debug(f'Making GET HTTP request to {url}')
        params['aid'] = self.agency_id
        if headers is None:
            headers = self.headers
        try:
            response = requests.get(url, params=params, auth=(
                self.user, self.password), headers=headers)
        except Exception as ex:
            logger.error(ex)
            sys.exit()
        if response.status_code not in [200, 201]:
            raise Exception(
                f'Error requesting Url: {url}, Response code: {response.status_code}. Error Message: {response.text}')
        return response.json()

    def sync_topic(self, domain, session_id, topic_name, page_size):
        offset = 0
        has_next_page = True
        while has_next_page:
            qr = self.fetch_sync_topic(
                domain, session_id, topic_name, page_size, offset)
            has_next_page = qr['hasNextPage']
            offset = offset + page_size

            # TODO - Plug in your logic to handle the query results here
            # for activity in qr['results']:
            #     print(activity)


def write_subscription_id(id_arg):
    config[env.upper()]['CAL_SUBSCRIPTION_ID'] = id_arg
    with open('../resources/config.json', 'w') as outfile:
        json.dump(config, outfile)


class SyncSubscriptionCommandType(Enum):
    Unknown = 1
    Create = 2
    Edit = 3
    Cancel = 4


class SyncSessionCommandType(Enum):
    Unknown = 1
    Create = 2
    RecordRead = 3
    Complete = 4
    Cancel = 5


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process Campaign API Sync Requests')
    parser.add_argument('--sync-topics', nargs=1, metavar='Comma Separated List of Topics',
                        help='Find existing active subscription, or create new one, and sync topics')

    args = parser.parse_args()

    # First make sure that the Campaign API is ready
    default_domain = 'cal'
    default_agency_id = 'SFO'
    campaign_api_client = CampaignApiClient(
        api_url, api_key, api_password, default_agency_id)
    sys_report = campaign_api_client.fetch_system_report()
    try:
        if sys_report['generalStatus'].lower() != 'ready':
            logger.error(
                'The Campaign API is not ready, current status is %s', sys_report['generalStatus'])
            sys.exit()
        if args.sync_topics:
            logger.info(
                'Subscribe and sync Filing Activities and Element Activities')

            # Create SyncSubscription or use existing SyncSubscription
            subscription_name = "My Sync Subscription"
            topics = args.sync_topics[0].split(",")
            sync_session = None
            feed_name = 'cal_v101'
            try:
                # Create SyncSubscription or use existing SyncSubscription with feed specified
                if not cal_subscription_id:
                    logger.info(
                        'Creating new subscription with name "%s" and feed name "%s"', subscription_name, feed_name)
                    subscription_response = campaign_api_client.create_subscription(
                        default_domain, feed_name, subscription_name)
                    subscription = subscription_response['subscription']
                    sub_id = subscription['id']

                    # Write Subscription ID to config.json file
                    write_subscription_id(sub_id)
                else:
                    sub_id = cal_subscription_id

                # Create SyncSession
                logger.info('Creating sync session')
                sync_session_response = campaign_api_client.create_session(
                    default_domain, sub_id)
                if sync_session_response['syncDataAvailable']:
                    sync_session = sync_session_response['session']
                    sess_id = sync_session['id']

                    # Sync all available topics
                    # for topic in ['filing-activities', 'element-activities', 'transaction-activities']:
                    for topic in topics:
                        page_size = 1000
                        logger.info(f'Synchronizing {topic}')
                        session_id = sync_session['id']
                        campaign_api_client.sync_topic(
                            default_domain, session_id, topic, page_size)

                    # Complete SyncSession
                    logger.info('Completing session')
                    campaign_api_client.execute_session_command(
                        default_domain, sess_id, SyncSessionCommandType.Complete.name)
                    logger.info('Sync complete')
                else:
                    logger.info(
                        'The Campaign API system has no sync data available')
            except Exception as ex:
                # Cancel Session on error
                if sync_session is not None:
                    campaign_api_client.execute_session_command(
                        default_domain, sync_session.id, SyncSessionCommandType.Cancel.name)
                logger.error('Error attempting to sync: %s', ex)
                sys.exit()
    except Exception as ex:
        logger.error('Error running Campaign API client %s', ex)
        sys.exit()
