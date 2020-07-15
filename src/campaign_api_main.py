#!/usr/bin/python

import sys
from campaign_api_client import CampaignApiClient, SyncSessionCommandType
from src import *


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
    5) Complete the SyncSession. This will be the end of the session
    """
    sync_session = None
    api_client = None
    domain = 'CAL'
    agency_id = 'SFO'
    try:
        logger.info(f'Starting {domain} Campaign API synchronization lifecycle for Agency {agency_id}')
        api_client = CampaignApiClient(
            api_url, api_key, api_password, agency_id)

        # Verify the system is ready
        sys_report = api_client.fetch_system_report()
        if sys_report['generalStatus'].lower() == 'ready':
            logger.info('Campaign API Sync is Ready')

            # Create SyncSubscription or use existing SyncSubscription with cal_v101 feed specified
            name = 'My Campaign API Feed'
            feed_name = 'cal_v101'
            if not cal_subscription_id:
                logger.info('Creating new subscription with name "%s" and feed name "%s"', name, feed_name)
                subscription_response = api_client.create_subscription(domain, feed_name, name)
                subscription = subscription_response['subscription']
                sub_id = subscription['id']

                # Write Subscription ID to config.json file
                write_config_param('CAL_SUBSCRIPTION_ID', sub_id)
            else:
                sub_id = cal_subscription_id

            # Create SyncSession
            logger.info('Creating sync session')
            sync_session_response = api_client.create_session(domain, sub_id)
            if sync_session_response['syncDataAvailable']:
                # Sync all available topics
                for topic in ['filing-activities', 'element-activities', 'transaction-activities', 'unitemized-transaction-activities']:
                    offset = 0
                    page_size = 1000
                    logger.info(f'Synchronizing {topic}')
                    sync_session = sync_session_response['session']
                    session_id = sync_session['id']
                    query_results = api_client.fetch_sync_topic(domain, session_id, topic, page_size, offset)
                    print_query_results(query_results)
                    while query_results['hasNextPage']:
                        offset = offset + page_size
                        query_results = api_client.fetch_sync_topic(domain, session_id, topic, page_size, offset)
                        print_query_results(query_results)

                # Complete SyncSession
                logger.info('Completing sync session')
                api_client.execute_session_command(domain, session_id, SyncSessionCommandType.Complete.name)

                logger.info('Synchronization lifecycle complete\n\n')
            else:
                logger.info('No Sync Data Available. Nothing to retrieve\n\n')
        else:
            logger.info('The Campaign API system status is %s and is not Ready', sys_report['generalStatus'])
    except Exception as ex:
        # Cancel Session on error
        if sync_session is not None:
            logger.info('Error occurred, canceling sync session')
            api_client.execute_session_command(domain, sync_session.id, SyncSessionCommandType.Cancel.name)
        logger.error('Error running CampaignApiClient: %s', ex)

    """
    This demonstrates the complete lifecycle of the Campaign API sync process.
    1) Create a Global SyncSubscription
    2) Create a Global SyncSession using the SyncSubscription. This will be the start of the session
    3) Synchronize Geocode Activities
    4) Synchronize Geo Link Activities
    5) Complete the SyncSession. This will be the end of the session
    """
    sync_session = None
    api_client = None
    domain = 'Global'
    try:
        logger.info(f'Starting {domain} Campaign API synchronization lifecycle for Agency {agency_id}')
        api_client = CampaignApiClient(
            api_url, api_key, api_password, agency_id)

        # Verify the system is ready
        sys_report = api_client.fetch_system_report()
        if sys_report['generalStatus'].lower() == 'ready':
            logger.info('Campaign API Sync is Ready')

            # Create SyncSubscription or use existing SyncSubscription with cal_v101 feed specified
            name = 'My Campaign API Feed'
            feed_name = 'global_geo_activity_v101'
            if not global_subscription_id:
                logger.info('Creating new subscription with name "%s" and feed name "%s"', name, feed_name)
                subscription_response = api_client.create_subscription(domain, feed_name, name)
                subscription = subscription_response['subscription']
                sub_id = subscription['id']

                # Write Subscription ID to config.json file
                write_config_param('GLOBAL_SUBSCRIPTION_ID', sub_id)
            else:
                sub_id = global_subscription_id

            # Create SyncSession
            logger.info('Creating sync session')
            sync_session_response = api_client.create_session(domain, sub_id)
            if sync_session_response['syncDataAvailable']:
                # Sync all available topics
                for topic in ['geocode-activities', 'link-activities']:
                    offset = 0
                    page_size = 1000
                    logger.info(f'Synchronizing {topic}')
                    sync_session = sync_session_response['session']
                    session_id = sync_session['id']
                    query_results = api_client.fetch_sync_topic(domain, session_id, topic, page_size, offset)
                    print_query_results(query_results)
                    while query_results['hasNextPage']:
                        offset = offset + page_size
                        query_results = api_client.fetch_sync_topic(domain, session_id, topic, page_size, offset)
                        print_query_results(query_results)

                # Complete SyncSession
                logger.info('Completing sync session')
                api_client.execute_session_command(domain, session_id, SyncSessionCommandType.Complete.name)

                # Optionally, Cancel the subscription. Only done when no further use of subscription is required
                logger.info('Canceling subscription')
                api_client.execute_subscription_command(domain, sub_id, SyncSessionCommandType.Cancel.name)

                logger.info('Synchronization lifecycle complete')
            else:
                logger.info('No Sync Data Available. Nothing to retrieve')
        else:
            logger.info('The Campaign API system status is %s and is not Ready', sys_report['generalStatus'])
    except Exception as ex:
        # Cancel Session on error
        if sync_session is not None:
            logger.info('Error occurred, canceling sync session')
            api_client.execute_session_command(domain, sync_session.id, SyncSessionCommandType.Cancel.name)
        logger.error('Error running CampaignApiClient: %s', ex)
    sys.exit()


def print_query_results(query_results):
    page_number = query_results["pageNumber"]
    page_size = query_results["limit"]
    total_count = query_results["totalCount"]
    results = query_results['results']
    current_record_count = (page_number-1)*page_size if page_number > 0 else page_number*page_size
    if total_count > 0:
        logger.info(f'Retrieving {current_record_count+1} - {current_record_count+len(results)} of {total_count} records')
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
