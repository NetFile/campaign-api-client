#!/usr/bin/python

import sys
import time


from src import *
from src.campaign_api_client import CampaignApiClient, SyncSessionCommandType


def write_config_param(param, value):
    config[env.upper()][param] = value
    with open('../resources/config.json', 'w') as outfile:
        json.dump(config, outfile)


def main():
    """
    This demonstrates the complete lifecycle of the Campaign API sync process.
    1) Create a Cal SyncSubscription
    2) Create a Cal SyncSession using the SyncSubscription. This will be the start of the session
    3) Synchronize Filing Activities
    4) Synchronize Element Activities
    5) Synchronize Transaction Activities
    6) Synchronize Unitemized Transaction Activities
    7) Complete the SyncSession. This will be the end of the session
    """

    domain = 'filing'
    agency_id = 'TEST'
    sync_session = None
    api_client = None
    try:
        logger.info(f'Starting {domain} Campaign API synchronization lifecycle for Agency {agency_id}')
        api_client = CampaignApiClient(api_url, api_key, api_password, agency_id)

        # Verify the system is ready
        sys_report = api_client.fetch_system_report()
        if sys_report['generalStatus'].lower() == 'ready':
            logger.info('Campaign API Sync is Ready')

            # Create new SyncSubscription
            name = 'My CAL Transactions Subscription'
            topics = ['element-activities']
            specification_org = "cal"
            element_classification = "UnItemizedTransaction"
            if not cal_subscription_id:
                logger.info('Creating new "%s" subscription with name "%s"', domain, name)
                # Filter for CAL Transactions only. Transactions are a property of Element-Activity, so filter that topic
                subscription_response = api_client.create_subscription(domain, name, agency_id, topics, element_classification, specification_org)
                sub_id = subscription_response['id']

                # Write Subscription ID to config.json file
                write_config_param('CAL_SUBSCRIPTION_ID', sub_id)
            else:
                sub_id = cal_subscription_id

            # Create SyncSession
            logger.info('Creating sync session')

            sync_lifecycle_start = time.time()
            if not api_client.peek_subscription(sub_id)['dataAvailable']:
                logger.info(f'The Campaign API system currently has no sync data available for subscription {sub_id}')
                return

            # while sync_session_response['syncDataAvailable']:
            while api_client.peek_subscription(sub_id)['dataAvailable']:
                session_start = time.time()
                # Sync specified topics
                # for topic in topics:
                for topic in topics:
                    topic_request_times = []
                    offset = 0
                    page_size = 1000
                    range_limit = 10000
                    logger.info(f'Synchronizing {topic} with elementClassification of {element_classification}')
                    sync_session_response = api_client.create_session(sub_id, range_limit)
                    sync_session = sync_session_response['session']
                    session_id = sync_session['id']
                    start_time = time.time()
                    query_results = api_client.read_sync_topic(domain, session_id, topic, page_size, offset)
                    end_time = time.time()
                    total_time = end_time-start_time
                    topic_request_times.append(total_time)
                    print_query_results(query_results, total_time)
                    while query_results['hasNextPage']:
                        offset = offset + page_size
                        start_time = time.time()
                        query_results = api_client.read_sync_topic(domain, session_id, topic, page_size, offset)
                        end_time = time.time()
                        total_time = end_time-start_time
                        topic_request_times.append(total_time)
                        print_query_results(query_results, total_time)
                    logger.info(f'Average time for {topic} sync read is {sum(topic_request_times) / len(topic_request_times)} seconds\n')

                logger.info('Completing sync session\n')

                # Show SyncSession Statistics
                session_end = time.time()
                logger.info(f'Total time for sync session: {session_end - session_start} seconds\n')

                api_client.execute_session_command(session_id, SyncSessionCommandType.Complete.name)

            logger.info(f'Synchronization lifecycle complete\n\n')
            sync_lifecycle_end = time.time()
            logger.info(f'Total time for synchronization lifecycle: {sync_lifecycle_end - sync_lifecycle_start} seconds')
        else:
            logger.info('The Campaign API system status is %s and is not Ready', sys_report['generalStatus'])
    except Exception as ex:
        logger.error('Error running CampaignApiClient: %s', ex)

        # Cancel Session on error
        if sync_session is not None:
            logger.info('Error occurred, canceling sync session')
            api_client.execute_session_command(sync_session['id'], SyncSessionCommandType.Cancel.name)

    sys.exit()


def print_query_results(query_results, seconds_to_complete):
    page_number = query_results["pageNumber"]
    page_size = query_results["limit"]
    total_count = query_results["totalCount"]
    results = query_results['results']
    current_record_count = (page_number-1)*page_size if page_number > 0 else page_number*page_size
    if total_count > 0:
        logger.info(f'Retrieved {current_record_count+1} - {current_record_count+len(results)} of {total_count} records in {seconds_to_complete} seconds')
        logger.debug(f'Total count: {total_count}')
        logger.debug(f'Offset: {query_results["offset"]}')
        logger.debug(f'Page Size: {page_size}')
        logger.debug(f'Page Number: {page_number}')
        logger.debug(f'Has Previous Page: {query_results["hasPreviousPage"]}')
        logger.debug(f'Has Next Page: {query_results["hasNextPage"]}')
        logger.debug('No Results Available') if len(results) == 0 else logger.debug('Results')
        for result in query_results['results']:
            logger.debug(f'\t{result}')
    else:
        logger.info('No records available')


if __name__ == '__main__':
    main()
