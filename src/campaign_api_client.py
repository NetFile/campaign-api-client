#!/usr/bin/python

from enum import Enum
import argparse
import requests

import sys
sys.path.append('../')
from src import *

logger = logging.getLogger(__name__)


class Routes:
    SYSTEM_REPORT = '/system'
    SYNC_FEED = '/cal/v101/sync/feeds'
    SYNC_SUBSCRIPTIONS = '/cal/v101/sync/subscriptions'
    SYNC_SESSIONS = '/cal/v101/sync/sessions'

    # First parameter is Session ID. Second parameter is Command Type
    SYNC_SESSION_COMMAND = '/cal/v101/sync/sessions/%s/commands/%s'

    # First parameter is Subscription ID. Second parameter is Command Type
    SYNC_SUBSCRIPTION_COMMAND = '/cal/v101/sync/subscriptions/%s/commands/%s'

    # Parameter is the Subscription ID
    FETCH_SUBSCRIPTION = '/cal/v101/sync/subscriptions/%s'

    # First parameter is the Root Filing NID
    FETCH_FILING = '/cal/v101/filings/%s'
    FETCH_EFILE_CONTENT = '/cal/v101/filings/%s/contents/efiling'
    QUERY_FILINGS = '/cal/v101/filings'

    # First parameter is the Element ID
    FETCH_FILING_ELEMENTS = '/cal/v101/filing-elements/%s'
    QUERY_FILING_ELEMENTS = '/cal/v101/filing-elements'


class CampaignApiClient:
    """Provides support for synchronizing local database with Campaign API filing data"""
    def __init__(self, base_url, api_key, api_password):
        self.headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        self.base_url = base_url
        self.user = api_key
        self.password = api_password

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
            logger.debug('\tComponent Build DateTime: %s', comp['buildDateTime'])
            logger.debug('\tComponent Build Version: %s', comp['buildVersion'])
        return sr

    def create_subscription(self, feed_name_arg, subscription_name_arg):
        logger.debug('Creating a SyncSubscription')
        url = self.base_url + Routes.SYNC_SUBSCRIPTIONS
        body = {
            'feedName': feed_name_arg,
            'name': subscription_name_arg
        }
        return self.post_http_request(url, body)

    def fetch_subscription(self, sub_id):
        logger.debug(f"Fetching SyncSubscription with id: {sub_id}")
        ext = Routes.SYNC_SUBSCRIPTION_COMMAND % sub_id
        url = self.base_url + ext
        return self.get_http_request(url)

    def execute_subscription_command(self, sub_id, subscription_command_type):
        logger.debug(f"Executing {subscription_command_type} SyncSubscription command")
        ext = Routes.SYNC_SUBSCRIPTION_COMMAND % (sub_id, subscription_command_type)
        url = self.base_url + ext
        body = {
            'id': sub_id
        }
        return self.post_http_request(url, body)

    def query_subscriptions(self, feed_id, limit=1000, offset=0):
        logger.debug('Retrieving available subscriptions\n')
        params = {'feedId': feed_id, 'status': 'Active', 'limit': limit, 'offset': offset}
        url = self.base_url + Routes.SYNC_SUBSCRIPTIONS
        return self.get_http_request(url, params)

    def create_session(self, sub_id):
        logger.debug(f'Creating a SyncSession using SyncSubscription {sub_id}')
        url = self.base_url + Routes.SYNC_SESSIONS
        body = {
            'subscriptionId': sub_id
        }
        return self.post_http_request(url, body)

    def execute_session_command(self, session_id, session_command_type):
        logger.debug(f'Executing {session_command_type} SyncSession command')
        url = self.base_url + Routes.SYNC_SESSION_COMMAND % (session_id, session_command_type)
        return self.post_http_request(url)

    def fetch_sync_topics(self, session_id, topic, limit=1000, offset=0):
        logger.debug(f'Fetching {topic} topic: offset={offset}, limit={limit}\n')
        params = {'limit': limit, 'offset': offset}
        url = f'{self.base_url}/{Routes.SYNC_SESSIONS}/{session_id}/{topic}'
        return self.get_http_request(url, params)

    def retrieve_sync_feeds(self):
        logger.debug('Retrieving SyncFeed')
        url = self.base_url + Routes.SYNC_FEED
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
        response = requests.get(url, params={'contentType': 'efile'}, auth=(self.user, self.password), headers=self.headers)
        if response.status_code not in [200, 201]:
            raise Exception(
                f'Error requesting Url: {url}, Response code: {response.status_code}. Error Message: {response.text}')
        file_content = response.text
        return file_content

    def post_http_request(self, url, body=None):
        logger.debug(f'Making POST HTTP request to {url}')
        try:
            response = requests.post(url, auth=(self.user, self.password), data=json.dumps(body), headers=self.headers)
        except Exception as ex:
            logger.info(ex)
            sys.exit()
        if response.status_code not in [200, 201]:
            raise Exception(
                f'Error requesting Url: {url}, Response code: {response.status_code}. Error Message: {response.text}')
        return response.json()

    def get_http_request(self, url, params=None, headers=None):
        logger.debug(f'Making GET HTTP request to {url}')
        if headers is None:
            headers = self.headers
        try:
            response = requests.get(url, params=params, auth=(self.user, self.password), headers=headers)
        except Exception as ex:
            logger.info(ex)
            sys.exit()
        if response.status_code not in [200, 201]:
            raise Exception(
                f'Error requesting Url: {url}, Response code: {response.status_code}. Error Message: {response.text}')
        return response.json()


def write_subscription_id(id_arg):
    config[env.upper()]['SUBSCRIPTION_ID'] = id_arg
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
    parser = argparse.ArgumentParser(description='Process Campaign API Sync Requests')
    parser.add_argument('--sync', nargs=1, metavar='Subscription_Name',
                        help='Find existing active subscription and sync available Feed Topics')
    parser.add_argument('--re-sync', nargs=1, metavar='subscription_id',
                        help='Find existing active subscription and sync available Feed Topics')
    parser.add_argument('--subscribe-and-sync', nargs=1, metavar='Subscription_Name',
                        help='Create a new subscription and Sync available Feed Topics')
    parser.add_argument('--database', nargs=1, metavar='[create or rebuild]',
                        help='Create or Rebuild a local database schema')
    parser.add_argument('--create-subscription', nargs=2, metavar=('feed_name', 'subscription_name'),
                        help='Create a new subscription')
    parser.add_argument('--cancel-subscription', nargs=1, metavar='subscription_id', help='Cancel an existing subscription')
    parser.add_argument('--create-session', nargs=1, metavar='subscription_id',
                        help='Create a new session')
    parser.add_argument('--session', nargs=2, metavar=('[cancel, or complete]', 'session_id'),
                        help='Cancel or complete a session')
    parser.add_argument('--sync-topic', nargs=2, metavar=('session_id', 'topic_name'),
                        help='sync a feed topic')
    parser.add_argument('--system-report', action='store_true',
                        help='Retrieve general system status')
    parser.add_argument('--feed', action='store_true',
                        help='retrieve available feeds')

    args = parser.parse_args()

    # First make sure that the Campaign API is ready
    campaign_api_client = CampaignApiClient(api_url, api_key, api_password)
    sys_report = campaign_api_client.fetch_system_report()
    try:
        if sys_report['generalStatus'].lower() != 'ready':
            logger.error('The Campaign API is not ready, current status is %s', sys_report['generalStatus'])
            sys.exit()
        if args.sync:
            logger.info('Subscribe and sync Filing Activities and Element Activities')
            # Retrieve available SyncFeeds
            feedsQr = campaign_api_client.retrieve_sync_feeds()

            # TODO - The feeds QR contains global_filing_v101, global_address_v101, cal_v101, and pubfi_v101. Is this correct given that we are getting the feeds from /cal/v101/sync/feeds?
            feed = feedsQr['results'][0]

            logger.info('Sync Feed retrieved: %s', feed)

            # Create SyncSubscription or use existing SyncSubscription with feed specified
            subscription_name = args.sync[0]
            sync_session = None
            try:
                # Create SyncSubscription or use existing SyncSubscription with feed specified
                if not subscription_id:
                    logger.info('Creating new subscription with name "%s" and feed name "%s"', subscription_name, feed['name'])
                    subscription_response = campaign_api_client.create_subscription(feed['name'], subscription_name)
                    subscription = subscription_response['subscription']

                    # Create SyncSession
                    logger.info('Creating sync session')
                    sub_id = subscription['id']

                    # Write Subscription ID to config.json file
                    write_subscription_id(sub_id)
                else:
                    sub_id = subscription_id

                # Create SyncSession
                logger.info('Creating new session')
                sync_session_response = campaign_api_client.create_session(sub_id)
                if sync_session_response['syncDataAvailable']:
                    sync_session = sync_session_response['session']
                    sess_id = sync_session['id']

                    # Sync all available topics
                    for topic in ['filing-activities', 'element-activities', 'transaction-activities']:
                        offset = 0
                        page_size = 50
                        logger.info(f'Synchronizing {topic}')
                        session_id = sync_session['id']
                        query_results = campaign_api_client.fetch_sync_topics(session_id, topic, page_size, offset)
                        while query_results['hasNextPage']:
                            offset = offset + page_size
                            query_results = campaign_api_client.fetch_sync_topics(session_id, topic, page_size, offset)

                    # Complete SyncSession
                    logger.info('Completing session')
                    campaign_api_client.execute_session_command(sess_id, SyncSessionCommandType.Complete.name)
                    logger.info('Sync complete')
                else:
                    logger.info('The Campaign API system has no sync data available')
            except Exception as ex:
                # Cancel Session on error
                if sync_session is not None:
                    campaign_api_client.execute_session_command(sync_session.id, SyncSessionCommandType.Cancel.name)
                logger.error('Error attempting to subscribe and sync: %s', ex)
                sys.exit()
        elif args.system_report:
            logger.info('Fetching system report')
            report = campaign_api_client.fetch_system_report()
            logger.info('General Status: %s', report.general_status)
            logger.info('System Name: %s', report.name)
            for component in report.components:
                logger.info('\tComponent Name: %s', component.name)
                logger.info('\tComponent Message: %s', component.message)
                logger.info('\tComponent status: %s', component.status)
        elif args.feed:
            logger.info('Retrieving sync feed')
            sync_feeds = campaign_api_client.retrieve_sync_feeds()
            sync_feed = sync_feeds[0]
            logger.info('Sync Feed retrieved: %s', sync_feed)
        elif args.create_subscription:
            feed_name = args.create_subscription[0]
            subscription_name = args.create_subscription[1]
            logger.info('Creating new sync subscription with name %s', subscription_name)
            sub_response = campaign_api_client.create_subscription(feed_name, subscription_name)
            logger.info('New sync subscription created: %s', sub_response.subscription)
        elif args.cancel_subscription:
            subscription_id = args.cancel_subscription[0]
            sub_response = campaign_api_client.execute_subscription_command(subscription_id, SyncSubscriptionCommandType.Cancel.name)
            logger.info('Canceled subscription: %s', sub_response.subscription)
        elif args.create_session:
            subscription_id = args.create_session[0]
            logger.info('Creating new sync session with subscription %s', subscription_id)
            sub_response = campaign_api_client.create_session(subscription_id)
            logger.info('New sync session created: %s', sub_response.session)
        elif args.session:
            command = args.session[0]
            if command == 'cancel':
                sess_id = args.session[1]
                sess_response = campaign_api_client.execute_session_command(sess_id, SyncSessionCommandType.Cancel.name)
                logger.info('Session canceled: %s', sess_response.session)
            elif command == 'complete':
                sess_id = args.session[1]
                try:
                    sess_response = campaign_api_client.execute_session_command(sess_id, SyncSessionCommandType.Complete.name)
                    logger.info('Sync Session complete: %s', sess_response.session)
                except Exception as ex:
                    logger.error('Error attempting to complete session with ID %s: %s', sess_id, ex)
        elif args.sync_topic:
            sess_id = args.sync_topic[0]
            topic_name = args.sync_topic[1]
            offset = 0
            page_size = 1000
            campaign_api_client.fetch_sync_topics(sess_id, topic_name, page_size, offset)

            query_results = campaign_api_client.fetch_sync_topics(sess_id, topic_name, page_size, offset)
            while query_results['hasNextPage']:
                offset = offset + page_size
                query_results = campaign_api_client.fetch_sync_topics(sess_id, topic_name, page_size, offset)
    except Exception as ex:
        logger.error('Error running Campaign API client %s', ex)
        sys.exit()
