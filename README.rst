NetFile Campaign API Sync Client
================================
Open source Python http client to synchronize with the Campaign API data provided by NetFile, Inc.

Basic of the Sync Process
    1. Check System Report to determine if API is Ready to receive requests
    2. Create a Sync Subscription (designed to be maintained across many sessions)
        * Can maintain existing subscription for many sessions
        * Can be Canceled if necessary
    3. Create a Sync Session
        * Associated with a specific Sync Subscription
        * Sync Session should be Completed when desired sync data has been retrieved
        * Can be canceled in which case no reads will be recorded on the back end
    4. Synchronize campaign records via available Sync Topics
        * Filing Activities, Element Activities, Transaction Activities
        * The topics will sync beginning with the sequence last completed session
    5. Complete or Cancel Sync Session
        * If you are satisfied with the sync data retrieved, then Complete the Sync Session
        * If you are not satisfied for any reason, Cancel the Sync Session
            * The next Sync Session for the subscription will start over from the sequence of the last completed session
    6. This will be the usual Sync life cycle.
        * However, the Sync Subscription can be Canceled if needed, and the process will begin from scratch

Included in the project is a script named campaign_api_main.py. This script contains example usage of the campaign_api_client.py file by demonstrating the complete process of syncing lobbyist data. This includes.
    - Check system status to verify the Campaign API is available and in a ready state
    - Creates a Sync Subscription
    - Creates a Sync Session for the Sync Subscription. This will track whether or not your sync feed is up to date, or if there is more data available to sync
    - Syncs Campaign information which includes: Filing Activities, Element Activities, Transaction Activities
    - If the process runs successfully, the script Completes the Sync Session. This will let the API know that you have received the Sync Feed data successfully.
    - If any errors are encountered while running the process, the script will Cancel the Sync Session. This will tell the API that you have not received the data successfully. The next sync session for the subscription will start the sync from the last known Completed Sync Session
    - Finally, the Sync Subscription is cancelled. This step is mostly for demonstration purposes, as a Sync Subscription is usually maintained across many Sync Sessions, and does not need to be disposed of unless there will be no subsequent Sync Sessions required.

Usage
-----
1) Create config.json file based on the included config.json.example file
    - Create copy of config.json.example file named config.json
    - Update the API_KEY and API_PASSWORD values with API credentials provided from NetFile
2) Use the campaign_api_client.py file as a command line utility
    * `python lobbyist_api_,main.py --sync`
        * This process will create a subscription and synchronize data for all topics specified. An existing subscription will be used if one has already been created
    * `python lobbyist_api_,main.py --help`

System Requirements
-------------------
Python 3
    - Tested using python 3.7
Required libraries (These can be installed using Pip (example: $ pip install requests)
    - Requests Library


Log level output and Lobbyist API target environment are specified in lobbyist_api_client/src/__init__.py file

**Provided and supported by NetFile, Inc. The largest provider of Campaign and SEI services in California.**

More information:

- [Website] (https://www.netfile.com)
