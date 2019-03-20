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















Open source Python library to synchronize a local database with the Campaign API data provided by NetFile, Inc.
This is a command line utility, written in Python, that allows a user to interact with NetFile, Inc.'s public Campaign API.

Basic of the Sync Process
    1. Check System Report to determine if API is Ready to receive requests
    2. Create a Sync Subscription (designed to be maintained across many sessions)
        * Can maintain existing subscription for many sessions
        * Can be Canceled if necessary
    3. Create a Sync Session
        * Associated with a specific Sync Subscription
        * Sync Session should be Completed when desired sync data has been retrieved
        * Can be canceled in which case no reads will be recorded on the back end
    4. Synchronize campaign records via available Sync Topics for the Cal_v101 Sync Feed.
        * The campaign record types include Filing-Activities, Element-Activities, and Transaction-Activities
        * The topics will sync beginning with the sequence last completed session
    5. Complete or Cancel Sync Session
        * If you are satisfied with the sync data retrieved, then Complete the Sync Session
        * If you are not satisfied for any reason, Cancel the Sync Session
            * The next Sync Session for the subscription will start over from the sequence of the last completed session
    6. This will be the usual Sync life cycle.
        * However, the Sync Subscription can be Canceled if needed, and the process will begin from scratch

Included in the project is a script named campaign_api_main.py. This script contains example usage of the Campaign API Client by demonstrating the complete process of syncing campaign data. This includes.
    - Rebuilds the local postgres database, which will remove existing data and re-generate sql schema
    - Check system status to verify the API is available and in a ready state
    - Retrieves Cal Sync Feed
    - Creates a Sync Subscription for the Cal Sync Feed
    - Creates a Sync Session for the Sync Subscription. This will track whether or not your sync feed is up to date, or if there is more data available to sync
    - Syncs Cal Feed which includes
        - Campaign Filing Activities
        - Elements of the Filing Activities known as Element Activities. An example might be a single Header, Transaction or Signature from a FPPC460 filing..
        - Transaction Activities, which are specific Element Activities that only include Transaction classification
    - If the process runs successfully, the script Completes the Sync Session. This will let the API know that you have received the Sync Feed data successfully.
    - If any errors are encountered while running the process, the script will Cancel the Sync Session. This will tell the API that you have not received the data successfully. The next sync session for the subscription will start the sync from the last known Completed Sync Session
    - Finally, the Sync Subscription is cancelled. This step is mostly for demonstration purposes, as a Sync Subscription is usually maintained across many Sync Sessions, and does not need to be disposed of unless there will be no subsequent Sync Sessions required.

Also included in the project are some simple unit test that demonstrate and validate the usage and behavior of the Campaign API Client and supporting classes.

Model classes have been created for all Sync operations. These classes have documentation to describe their function in the system.

System Requirements
-------------------
PostgreSQL Database
    - Tested using version 9.6
Python 3
    - Tested using python 3.7
Required libraries (These can be installed using Pip (example: $ pip install requests)
    - Requests Library
    - Psycopg2 Library

Usage
-----
1) Create config.json file based on config.json.example file
    - Create copy of config.json.example file named config.json
    - Update the DB_HOST variable with the database host name
    - Update the DB_USER, DB_PASSWORD with values used by your local installation of PostgreSQL database
    - Update the API_KEY, API_PASSWORD values with credentials provided from NetFile
2) Use the campaign_api_client.py file as a command line utility to perform necessary operations
    - For list of available commands: `python campaign_api_client.py --help`
3) Create local postgres database that will contain the synchronized Campaign data
    - First manually create a local postgres database that matches the DB_NAME value in config.json file. (The default is 'campaign-api-sync')
    - Create schema the first time. example: `python campaign_api_client.py --database create`
    - Rebuild the schema (drop all tables and re-create from SQL schema file)
        example: `python campaign_api_client.py --database rebuild`
4) View available Sync Feeds and Sync Topics:
    - example: `python campaign_api_client.py --feed`
5) Create a new Sync Subscription for a Sync Feed. The subscription can be maintained over the long term if desired, and does not need to be re-created. Command arguments are an existing Feed Name and user provided Subscription Name:
    - example: `python campaign_api_client.py --create-subscription cal_V101 Test_Filing_Activity_Sub`
6) Create a new Sync Session associated with a Sync Subscription by providing the subscription ID as input argument. The lifecycle of the Sync Session is only for a single Sync cycle, and will be set to completed when finished, or canceled if necessary.
    - example: `python campaign_api_client.py --create-session 48aae322-a0be-42c3-b010-61534a8aa964`
7) Once the Sync Session is created, synchronize the Feed Topics to the local database by providing the session ID and topic name
    - example 1: `python campaign_api_client.py --sync-topic 05af361b-6c4b-489f-9673-4cfe7f189ddd filing-activities`
    - example 2: `python campaign_api_client.py --sync-topic 05af361b-6c4b-489f-9673-4cfe7f189ddd element-activities`
    - **Note: The local database should now have the latest data available through the API.**
8) Optionally Cancel the Sync Session. User provides the Session ID. No reads of the Sync Session will be recorded on the back-end.
    - example: `python campaign_api_client.py --session cancel ebcb9151-067e-47de-be67-20e256b79d73`
9) Complete the Sync Session when done with desired Sync Topics. User provides the Session ID
    - example: `python campaign_api_client.py --session complete 05af361b-6c4b-489f-9673-4cfe7f189ddd`
    - **Note: The Sync process is now Complete**
10) Optionally Cancel the Sync Subscription. This subscription will no longer be available for any further operations. User provides the Subscription ID

    - example: `python campaign_api_client.py --cancel-subscription 48aae322-a0be-42c3-b010-61534a8aa964`

Log level output and Campaign API target environment are specified in campaign_api_client/src/__init__.py file

**Provided and supported by NetFile, Inc. The largest provider of Campaign and SEI services in California.**

More information:

- [Website] (https://www.netfile.com)
